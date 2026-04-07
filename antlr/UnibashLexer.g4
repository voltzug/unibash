lexer grammar UnibashLexer;

// #0. whitespace and comments
NEWLINE
    : '\r'? '\n'
    ;
WS
    : [ \t]+ -> skip
    ;
COMMENT
    : '#' ~[\r\n]* -> channel(HIDDEN)
    ;

// #1. host def
HOST : 'host';
VIA  : 'via';
SSH  : 'ssh';
TELNET : 'telnet';
PORT : 'port';
USER : 'user';
PASSWORD : 'password' | 'pass';
KEY  : 'key';

// #2. ranges and groups
RANGE  : 'range';
GROUP  : 'group';
LBRACK : '[';
RBRACK : ']';
COMMA  : ',';
DOTDOT : '..';

// #3. variables
SET    : 'set';
ASSIGN : '=';

// #4. ping
PING    : 'ping';
COUNT   : 'count';
TIMEOUT : 'timeout';

// #5. connect
CONNECT : 'connect';

// #6. inspect
INSPECT : 'inspect';
SHOW    : 'show';
OS      : 'os';
MEMORY  : 'memory';
DISK    : 'disk';
CPU     : 'cpu';
NETWORK : 'network';

// #7. process management
RESTART : 'restart';
STOP    : 'stop';
START   : 'start';
STATUS  : 'status';
PROCESS : 'process';
ON      : 'on';

// #8. file operations
DOWNLOAD : 'download';
UPLOAD   : 'upload';
COPY     : 'copy';
FROM     : 'from';
TO       : 'to';
PATH     : 'path';

// #9. IP configuration
ADD       : 'add';
IP        : 'ip';
INTERFACE : 'interface';

// #10. DHCP configuration
CONFIGURE : 'configure';
DHCP      : 'dhcp';
SUBNET    : 'subnet';
GATEWAY   : 'gateway';
DNS       : 'dns';

// #11. DNS configuration
ZONE       : 'zone';
RECORD     : 'record';
FORWARDERS : 'forwarders';

// #12. conditionals
IF  : 'if';
ELSE: 'else';
EQ  : '==';
NEQ : '!=';

// #13. foreach
FOREACH : 'foreach';
IN      : 'in';
WHERE   : 'where';

// #14. remote execution (on)
LBRACE : '{';
RBRACE : '}';

// #15. remote execution (via)
RUN : 'run';

// #16. HTTP
HTTP   : 'http';
GET    : 'get';
POST   : 'post';
PUT    : 'put';
DELETE : 'delete';
PATCH  : 'patch';
HEAD   : 'head';
SAVE   : 'save';
HEADER : 'header';
BODY   : 'body';

// #17. exec
EXEC : 'exec';

// #18. print
PRINT : 'print';

// #0. core separators
PIPE : '|';
SEMI : ';';
REDIR_APP : '>>';
REDIR_OUT : '>';
REDIR_IN  : '<';

// #0. strings and literals
SQUOTE_STRING
    : '\'' ( '\'\'' | ~['\r\n] )* '\''
    ;
DQUOTE_STRING
    : '"' ( '\\"' | '\\' . | ~["\\\r\n] )* '"'
    ;
IP4ADDR
    : IP4ADDR_DIGIT '.' IP4ADDR_DIGIT '.' IP4ADDR_DIGIT '.' IP4ADDR_DIGIT
    ;
fragment IP4ADDR_DIGIT
    : DIGIT (DIGIT)? (DIGIT)?
    ;
IP6ADDR
    : HEXDIGIT+ ':' HEXDIGIT+ (':' HEXDIGIT+)*
    ;
NUMBER
    : DIGIT+
    ;
fragment HEXDIGIT
    : [0-9a-fA-F]
    ;
fragment DIGIT
    : [0-9]
    ;
IDENT
    : LETTER (LETTER | DIGIT)*
    ;
fragment LETTER
    : [a-zA-Z_]
    ;
