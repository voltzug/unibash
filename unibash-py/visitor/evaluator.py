from typing import Any, List

from executor.parrot.executor import ParrotExecutor
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

    def __init__(self, context: RuntimeContext):
        super().__init__()
        self.context = context
        self.resolver = TargetResolver(context)
        self.executor = ParrotExecutor()

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

        for t in targets:
            self.executor.ping(t, count=count, timeout=timeout)

    def visitConnect_stmt(self, ctx: UnibashParser.Connect_stmtContext):
        targets = self._get_targets(ctx.target())
        for t in targets:
            self.executor.connect(t)

    def visitInspect_stmt(self, ctx: UnibashParser.Inspect_stmtContext):
        targets = self._get_targets(ctx.target())
        category = ctx.inspect_category().getText() if ctx.inspect_category() else None
        results = []
        for t in targets:
            results.append(self.executor.inspect(t, category=category))
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

        for t in targets:
            if action == "start":
                self.executor.start(process_name, t)
            elif action == "stop":
                self.executor.stop(process_name, t)
            elif action == "restart":
                self.executor.restart(process_name, t)
            else:
                self.executor.status(process_name, t)

    def visitPrint_stmt(self, ctx: UnibashParser.Print_stmtContext):
        if ctx.inspect_stmt():
            result = self.visit(ctx.inspect_stmt())
            self.executor.print(result)
        else:
            values = [str(self.visit(val)) for val in ctx.value()]
            self.executor.print(" ".join(values))
