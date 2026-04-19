from typing import Any, List

from executor.base.executor import BaseExecutor
from gen.UnibashParser import UnibashParser
from gen.UnibashParserVisitor import UnibashParserVisitor
from runtime.context import RuntimeContext
from runtime.models import Group, Host, Range
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
                    host.protocol = opt_ctx.protocol().getText()
                else:
                    host.protocol = self.visit(opt_ctx.name())
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
        targets = self._get_targets(ctx.target()) if ctx.target() else []
        action = "status"  # default
        if ctx.START():
            action = "start"
        elif ctx.STOP():
            action = "stop"
        elif ctx.RESTART():
            action = "restart"

        process_name = self.visit(ctx.value()) if ctx.value() else "unknown"

        results = []
        for t in targets:
            if action == "start":
                res = self.executor.start(process_name, t)
            elif action == "stop":
                res = self.executor.stop(process_name, t)
            elif action == "restart":
                res = self.executor.restart(process_name, t)
            else:
                res = self.executor.status(process_name, t)

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
        pass

    def visitDns_config(self, ctx: UnibashParser.Dns_configContext):
        pass

    def visitIf_stmt(self, ctx: UnibashParser.If_stmtContext):
        # Missing evaluation logic
        pass

    def visitForeach_stmt(self, ctx: UnibashParser.Foreach_stmtContext):
        # Missing evaluation logic
        pass

    def visitOn_block(self, ctx: UnibashParser.On_blockContext):
        # Missing evaluation logic
        pass

    def visitVia_block(self, ctx: UnibashParser.Via_blockContext):
        # Missing evaluation logic
        pass

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
        pass

    def visitOperand(self, ctx: UnibashParser.OperandContext):
        pass

    def visitTarget(self, ctx: UnibashParser.TargetContext):
        pass
