from typing import Any, List

from executor.base.executor import BaseExecutor
from gen.UnibashParser import UnibashParser
from gen.UnibashParserVisitor import UnibashParserVisitor
from runtime.context import RuntimeContext
from runtime.models import Group, Host, Protocol, Range
from runtime.resolver import TargetResolver


class UnibashEvaluator(UnibashParserVisitor):
    """
    Evaluates the Unibash parse tree, modifying the runtime context
    and delegating execution to the appropriate executors.
    """

    def __init__(self, context: RuntimeContext, executor=None):
        super().__init__()
        self.context = context
        self.resolver = TargetResolver(context)
        self.executor = executor or BaseExecutor()

    # --- Helpers ---

    def strip_quotes(self, text: str) -> str:
        """Removes single or double quotes from a string literal."""
        if text.startswith('"') and text.endswith('"'):
            return text[1:-1]
        if text.startswith("'") and text.endswith("'"):
            return text[1:-1]
        return text

    # --- Basic values ---

    def visitString_literal(self, ctx: UnibashParser.String_literalContext) -> str:
        return self.strip_quotes(ctx.getText())

    def visitAddr(self, ctx: UnibashParser.AddrContext) -> str:
        return ctx.getText()

    def visitName(self, ctx: UnibashParser.NameContext) -> str:
        if ctx.string_literal():
            return self.visit(ctx.string_literal())
        return ctx.getText()

    def visitValue(self, ctx: UnibashParser.ValueContext) -> Any:
        if ctx.NUMBER():
            return int(ctx.getText())
        if ctx.addr():
            return self.visit(ctx.addr())
        if ctx.name():
            # If it's a raw identifier, we try to resolve it from variables,
            # otherwise just return the identifier string
            name = self.visit(ctx.name())
            try:
                # Attempt to retrieve from context if it exists
                return self.context.get_variable(name)
            except Exception:
                return name
        return ctx.getText()

    def visitList_literal(self, ctx: UnibashParser.List_literalContext) -> List[Any]:
        return [self.visit(val) for val in ctx.value()]

    # --- Declarations ---

    def visitHost_decl(self, ctx: UnibashParser.Host_declContext):
        name = ctx.IDENT().getText()

        if ctx.addr():
            address = self.visit(ctx.addr())
        else:
            address = self.visit(ctx.string_literal())

        host = Host(name=name, address=address)

        # Parse options
        for opt_ctx in ctx.host_option():
            if opt_ctx.VIA():
                if opt_ctx.protocol():
                    proto_text = opt_ctx.protocol().getText().lower()
                else:
                    proto_text = str(self.visit(opt_ctx.name())).lower()
                try:
                    host.protocol = Protocol(proto_text)
                except ValueError:
                    host.protocol = proto_text
            elif opt_ctx.PORT():
                host.port = int(opt_ctx.NUMBER().getText())
            elif opt_ctx.USER():
                host.user = self.visit(opt_ctx.name())
            elif opt_ctx.PASSWORD():
                host.password = self.visit(opt_ctx.name())
            elif opt_ctx.KEY():
                host.key = self.visit(opt_ctx.name())

        self.context.register_host(host)
        return host

    def visitRange_decl(self, ctx: UnibashParser.Range_declContext):
        name = ctx.IDENT().getText()
        expr_ctx = ctx.range_expr()

        ips = []
        if expr_ctx.DOTDOT():
            start = self.visit(expr_ctx.value(0))
            end = self.visit(expr_ctx.value(1))
            # Just store the string representation for now, or generate IPs if they are numeric
            ips = [f"{start}..{end}"]
        elif expr_ctx.list_literal():
            ips = self.visit(expr_ctx.list_literal())

        rng = Range(name=name, ips=[str(ip) for ip in ips])
        self.context.register_range(rng)
        return rng

    def visitGroup_decl(self, ctx: UnibashParser.Group_declContext):
        name = ctx.IDENT().getText()
        members = [str(m) for m in self.visit(ctx.list_literal())]

        # When parsing `group production = [webserver, dbserver]`
        # members are parsed as identifiers (values).
        group = Group(name=name, members=members)
        self.context.register_group(group)
        return group

    def visitSet_stmt(self, ctx: UnibashParser.Set_stmtContext):
        name = ctx.IDENT().getText()
        value = self.visit(ctx.value())
        self.context.set_variable(name, value)
        return value

    # --- Core Actions (To be wired to executors) ---

    def _get_targets(self, target_ctx) -> List[Host]:
        target_name = target_ctx.IDENT().getText()
        return self.resolver.resolve(target_name)

    def _eval_block(self, block_ctx):
        results = []
        for stmt in block_ctx.statement():
            results.append(self.visit(stmt))
        return results

    def _eval_condition(self, left, right, is_eq: bool) -> bool:
        def normalize(val):
            if isinstance(val, str):
                return val.strip().casefold()
            if isinstance(val, list):
                return [normalize(item) for item in val]
            return val

        left_cmp = normalize(left)
        right_cmp = normalize(right)

        if isinstance(left_cmp, list) and isinstance(right_cmp, list):
            result = left_cmp == right_cmp
        elif isinstance(left_cmp, list) and not isinstance(right_cmp, list):
            result = right_cmp in left_cmp
        elif not isinstance(left_cmp, list) and isinstance(right_cmp, list):
            result = left_cmp in right_cmp
        else:
            result = left_cmp == right_cmp

        return result if is_eq else not result

    def visitPing_stmt(self, ctx: UnibashParser.Ping_stmtContext):
        targets = self._get_targets(ctx.target())
        count = int(ctx.NUMBER(0).getText()) if ctx.COUNT() else 4
        timeout = (
            int(ctx.NUMBER(1).getText())
            if ctx.TIMEOUT() and len(ctx.NUMBER()) > 1
            else 5
        )
        if ctx.TIMEOUT() and ctx.IDENT():
            timeout = int(self.context.get_variable(ctx.IDENT().getText()))

        results = []
        for t in targets:
            res = self.executor.ping(t, count=count, timeout=timeout)
            if res is not None:
                self.executor.print(res)
            results.append(res)
        return results

    def visitConnect_stmt(self, ctx: UnibashParser.Connect_stmtContext):
        targets = self._get_targets(ctx.target())
        for t in targets:
            self.executor.connect(t)

    def visitInspect_stmt(self, ctx: UnibashParser.Inspect_stmtContext):
        targets = self._get_targets(ctx.target())
        category = ctx.inspect_category().getText() if ctx.inspect_category() else None
        results = []
        for t in targets:
            res = self.executor.inspect(t, category=category)
            if res is not None:
                self.executor.print(res)
            results.append(res)
        return results

    def visitProcess_stmt(self, ctx: UnibashParser.Process_stmtContext):
        implicit = getattr(self, "_implicit_target", None)
        if ctx.target():
            targets = self._get_targets(ctx.target())
        elif implicit is not None:
            targets = [implicit]
        else:
            targets = []

        action = "status"  # default
        if ctx.START():
            action = "start"
        elif ctx.STOP():
            action = "stop"
        elif ctx.RESTART():
            action = "restart"

        process_name = self.visit(ctx.value()) if ctx.value() else None

        results = []
        for t in targets:
            proc_name = process_name
            if proc_name is None:
                if hasattr(t, "backend_process_name"):
                    proc_name = t.backend_process_name()
                else:
                    proc_name = getattr(t, "protocol", "unknown")

            if action == "start":
                res = self.executor.start(proc_name, t)
            elif action == "stop":
                res = self.executor.stop(proc_name, t)
            elif action == "restart":
                res = self.executor.restart(proc_name, t)
            else:
                res = self.executor.status(proc_name, t)

            if res is not None:
                self.executor.print(res)
            results.append(res)
        return results

    def visitPrint_stmt(self, ctx: UnibashParser.Print_stmtContext):
        if ctx.inspect_stmt():
            result = self.visit(ctx.inspect_stmt())
            self.executor.print(result)
        else:
            values = [str(self.visit(val)) for val in ctx.value()]
            self.executor.print(" ".join(values))

    def visitDownload_stmt(self, ctx: UnibashParser.Download_stmtContext):
        remote_path = self.visit(ctx.name(0))
        local_path = self.visit(ctx.name(1))
        targets = self._get_targets(ctx.target())
        results = []
        for t in targets:
            results.append(self.executor.download(remote_path, local_path, t))
        return results

    def visitUpload_stmt(self, ctx: UnibashParser.Upload_stmtContext):
        local_path = self.visit(ctx.name(0))
        remote_path = self.visit(ctx.name(1))
        targets = self._get_targets(ctx.target())
        results = []
        for t in targets:
            results.append(self.executor.upload(local_path, remote_path, t))
        return results

    def visitCopy_stmt(self, ctx: UnibashParser.Copy_stmtContext):
        src_path = self.visit(ctx.name(0))
        dest_path = self.visit(ctx.name(1))
        src_targets = self._get_targets(ctx.target(0))
        dest_targets = self._get_targets(ctx.target(1))
        results = []
        for s in src_targets:
            for d in dest_targets:
                results.append(self.executor.copy(src_path, s, dest_path, d))
        return results

    def visitIp_config_stmt(self, ctx: UnibashParser.Ip_config_stmtContext):
        ip = str(self.visit(ctx.value(0)))
        interface = str(self.visit(ctx.value(1)))
        targets = self._get_targets(ctx.target())

        is_add = ctx.ADD() is not None
        results = []
        for t in targets:
            if is_add:
                results.append(self.executor.add_ip(ip, interface, t))
            else:
                results.append(self.executor.set_ip(ip, interface, t))
        return results

    def visitDhcp_config(self, ctx: UnibashParser.Dhcp_configContext):
        targets = self._get_targets(ctx.target())
        block = ctx.dhcp_block()
        config = {}

        if block:
            for entry in block.dhcp_entry():
                if entry.SUBNET():
                    config["subnet"] = self.visit(entry.value())
                elif entry.RANGE():
                    range_expr = entry.range_expr()
                    if range_expr.DOTDOT():
                        start = self.visit(range_expr.value(0))
                        end = self.visit(range_expr.value(1))
                        config["range"] = f"{start}..{end}"
                    elif range_expr.list_literal():
                        config["range"] = self.visit(range_expr.list_literal())
                elif entry.GATEWAY():
                    config["gateway"] = self.visit(entry.value())
                elif entry.DNS():
                    config["dns"] = self.visit(entry.list_literal())

        results = []
        for t in targets:
            results.append(self.executor.configure_dhcp(config, t))
        return results

    def visitDns_config(self, ctx: UnibashParser.Dns_configContext):
        targets = self._get_targets(ctx.target())
        block = ctx.dns_block()
        config = {"records": []}

        if block:
            for entry in block.dns_entry():
                if entry.ZONE():
                    config["zone"] = self.visit(entry.value(0))
                elif entry.RECORD():
                    vals = [self.visit(v) for v in entry.value()]
                    record_type = str(vals[0]) if len(vals) > 0 else ""
                    record_name = str(vals[1]) if len(vals) > 1 else ""
                    record_value = str(vals[2]) if len(vals) > 2 else None
                    config["records"].append(
                        {
                            "type": record_type,
                            "name": record_name,
                            "value": record_value,
                        }
                    )
                elif entry.FORWARDERS():
                    config["forwarders"] = self.visit(entry.list_literal())

        results = []
        for t in targets:
            results.append(self.executor.configure_dns(config, t))
        return results

    def visitIf_stmt(self, ctx: UnibashParser.If_stmtContext):
        conditions = ctx.condition()
        blocks = ctx.block()

        if not blocks:
            return None

        for idx, cond in enumerate(conditions):
            if self.visit(cond):
                return self._eval_block(blocks[idx])

        if len(blocks) > len(conditions):
            return self._eval_block(blocks[-1])

        return None

    def visitForeach_stmt(self, ctx: UnibashParser.Foreach_stmtContext):
        var_name = ctx.IDENT().getText()
        targets = self._get_targets(ctx.target())
        cond_ctx = ctx.foreach_condition() if ctx.WHERE() else None

        results = []
        sentinel = object()
        prev_value = self.context.variables.get(var_name, sentinel)
        prev_implicit = getattr(self, "_implicit_target", None)

        try:
            for target in targets:
                self.context.variables[var_name] = target
                self._implicit_target = target

                if cond_ctx and not self.visit(cond_ctx):
                    continue

                results.extend(self._eval_block(ctx.block()))
        finally:
            self._implicit_target = prev_implicit
            if prev_value is sentinel:
                self.context.variables.pop(var_name, None)
            else:
                self.context.variables[var_name] = prev_value

        return results

    def visitOn_block(self, ctx: UnibashParser.On_blockContext):
        targets = self._get_targets(ctx.target())
        results = []

        prev_target = getattr(self, "_implicit_target", None)
        sentinel = object()
        prev_on = self.context.variables.get("__on__", sentinel)
        try:
            for target in targets:
                self._implicit_target = target
                self.context.variables["__on__"] = target
                results.extend(self._eval_block(ctx.block()))
        finally:
            self._implicit_target = prev_target
            if prev_on is sentinel:
                self.context.variables.pop("__on__", None)
            else:
                self.context.variables["__on__"] = prev_on

        return results

    def visitVia_block(self, ctx: UnibashParser.Via_blockContext):
        via_targets = self._get_targets(ctx.target())
        results = []

        prev_via = getattr(self, "_via_target", None)
        sentinel = object()
        prev_via_var = self.context.variables.get("__via__", sentinel)
        try:
            for target in via_targets:
                self._via_target = target
                self.context.variables["__via__"] = target
                results.extend(self._eval_block(ctx.block()))
        finally:
            self._via_target = prev_via
            if prev_via_var is sentinel:
                self.context.variables.pop("__via__", None)
            else:
                self.context.variables["__via__"] = prev_via_var

        return results

    def visitHttp_stmt(self, ctx: UnibashParser.Http_stmtContext):
        method = ctx.http_method().getText().lower()
        url = str(self.visit(ctx.value(0)))

        headers = {}
        body = None

        if ctx.http_block():
            block_data = self.visit(ctx.http_block())
            headers = block_data.get("headers", {})
            body = block_data.get("body")

        if method == "get":
            result = self.executor.get(url, headers)
        elif method == "head":
            result = self.executor.head(url, headers)
        elif method == "post":
            result = self.executor.post(url, headers, body)
        elif method == "put":
            result = self.executor.put(url, headers, body)
        elif method == "delete":
            result = self.executor.delete(url, headers)
        elif method == "patch":
            result = self.executor.patch(url, headers, body)
        else:
            result = None

        if ctx.SAVE() and result:
            save_path = str(self.visit(ctx.value(1)))
            try:
                with open(save_path, "w") as f:
                    f.write(str(result))
            except Exception as e:
                print(f"Error saving to {save_path}: {e}")
        elif result is not None:
            self.executor.print(result)

        return result

    def visitHttp_block(self, ctx: UnibashParser.Http_blockContext):
        data = {"headers": {}, "body": None}
        for entry in ctx.http_entry():
            key, val = self.visit(entry)
            if key == "header":
                data["headers"][val[0]] = val[1]
            elif key == "body":
                data["body"] = val
        return data

    def visitHttp_entry(self, ctx: UnibashParser.Http_entryContext):
        if ctx.HEADER():
            return (
                "header",
                (str(self.visit(ctx.value(0))), str(self.visit(ctx.value(1)))),
            )
        if ctx.BODY():
            return ("body", str(self.visit(ctx.value(0))))

    def visitExec_stmt(self, ctx: UnibashParser.Exec_stmtContext):
        targets = self._get_targets(ctx.target())
        commands = []
        if ctx.value():
            commands.append(str(self.visit(ctx.value())))
        elif ctx.exec_block():
            commands.extend(self.visit(ctx.exec_block()))

        results = []
        for t in targets:
            res = self.executor.execute(commands, t)
            if res is not None:
                self.executor.print(res)
            results.append(res)
        return results

    def visitExec_block(self, ctx: UnibashParser.Exec_blockContext):
        return [self.visit(line) for line in ctx.exec_line()]

    def visitExec_line(self, ctx: UnibashParser.Exec_lineContext):
        return self.visit(ctx.string_literal())

    def visitCondition(self, ctx: UnibashParser.ConditionContext):
        left = self.visit(ctx.operand(0))
        right = self.visit(ctx.operand(1))
        return self._eval_condition(left, right, ctx.EQ() is not None)

    def visitForeach_condition(self, ctx: UnibashParser.Foreach_conditionContext):
        left = self.visit(ctx.foreach_operand(0))
        right = self.visit(ctx.foreach_operand(1))
        return self._eval_condition(left, right, ctx.EQ() is not None)

    def visitForeach_operand(self, ctx: UnibashParser.Foreach_operandContext):
        if ctx.OS():
            target_ctx = ctx.target()
            if target_ctx is None:
                implicit = getattr(self, "_implicit_target", None)
                if implicit is None:
                    return None
                if getattr(implicit, "os_type", None):
                    return implicit.os_type
                os_val = self.executor.inspect(implicit, category="os")
                if os_val is not None:
                    implicit.os_type = os_val
                return os_val

            targets = self._get_targets(target_ctx)
            if not targets:
                return None
            os_values = []
            for target in targets:
                if getattr(target, "os_type", None):
                    os_values.append(target.os_type)
                    continue
                os_val = self.executor.inspect(target, category="os")
                if os_val is not None:
                    target.os_type = os_val
                os_values.append(os_val)
            if len(os_values) == 1:
                return os_values[0]
            return os_values

        return self.visit(ctx.value())

    def visitOperand(self, ctx: UnibashParser.OperandContext):
        if ctx.OS():
            target_ctx = ctx.target()
            if target_ctx is None:
                implicit = getattr(self, "_implicit_target", None)
                if implicit is None:
                    return None
                if getattr(implicit, "os_type", None):
                    return implicit.os_type
                os_val = self.executor.inspect(implicit, category="os")
                if os_val is not None:
                    implicit.os_type = os_val
                return os_val

            targets = self._get_targets(target_ctx)
            if not targets:
                return None
            os_values = []
            for target in targets:
                if getattr(target, "os_type", None):
                    os_values.append(target.os_type)
                    continue
                os_val = self.executor.inspect(target, category="os")
                if os_val is not None:
                    target.os_type = os_val
                os_values.append(os_val)
            if len(os_values) == 1:
                return os_values[0]
            return os_values

        return self.visit(ctx.value())

    def visitTarget(self, ctx: UnibashParser.TargetContext):
        return ctx.IDENT().getText()
