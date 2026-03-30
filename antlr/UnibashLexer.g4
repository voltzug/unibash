lexer grammar UnibashLexer;

NEWLINE         : '\r'? '\n' ;
WS              : [ \t]+ -> skip ;
COMMENT         : '#' ~[\r\n]* -> skip ;

HOST            : 'host' ;
RANGE           : 'range' ;
GROUP           : 'group' ;
VIA             : 'via' ;
SSH             : 'ssh' ;
TELNET          : 'telnet' ;
PORT            : 'port' ;
USER            : 'user' ;
PASSWORD        : 'password' ;
KEY             : 'key' ;

PING            : 'ping' ;
CONNECT         : 'connect' ;
COUNT           : 'count' ;
TIMEOUT         : 'timeout' ;

RESTART         : 'restart' ;
STOP            : 'stop' ;
START           : 'start' ;
STATUS          : 'status' ;
PROCESS         : 'process' ;

DOWNLOAD        : 'download' ;
UPLOAD          : 'upload' ;
COPY            : 'copy' ;
FROM            : 'from' ;
TO              : 'to' ;
PATH            : 'path' ;

INSPECT         : 'inspect' ;
SHOW            : 'show' ;
OS              : 'os' ;
MEMORY          : 'memory' ;
DISK            : 'disk' ;
CPU             : 'cpu' ;
NETWORK         : 'network' ;

SET             : 'set' ;
ADD             : 'add' ;
IP              : 'ip' ;
INTERFACE       : 'interface' ;
CONFIGURE       : 'configure' ;
DHCP            : 'dhcp' ;
DNS             : 'dns' ;
SUBNET          : 'subnet' ;
GATEWAY         : 'gateway' ;
FORWARDERS      : 'forwarders' ;
ZONE            : 'zone' ;
RECORD          : 'record' ;

IF              : 'if' ;
ELSE            : 'else' ;
FOREACH         : 'foreach' ;
IN              : 'in' ;
WHERE           : 'where' ;

ON              : 'on' ;
RUN             : 'run' ;

HTTP            : 'http' ;
GET             : 'get' ;
POST            : 'post' ;
PUT             : 'put' ;
DELETE          : 'delete' ;
PATCH           : 'patch' ;
HEADER          : 'header' ;
BODY            : 'body' ;
SAVE            : 'save' ;


EXEC            : 'exec' ;
PRINT           : 'print' ;


LBRACE          : '{' ;
RBRACE          : '}' ;
LBRACKET        : '[' ;
RBRACKET        : ']' ;
EQUALS          : '==' ;
NOT_EQ          : '!=' ;
ASSIGN          : '=' ;
COMMA           : ',' ;
DOT_DOT         : '..' ;
SEMI            : ';' ;
PIPE            : '|' ;

IP_ADDR         : DIGIT+ '.' DIGIT+ '.' DIGIT+ '.' DIGIT+ ;
NUMBER          : DIGIT+ ;
SQUOTE_STR      : '\'' ( '\\\'' | ~['\r\n] )* '\'' ;
DQUOTE_STR      : '"'  ( '\\"'  | '\\' . | ~["\\\r\n] )* '"' ;

IDENT           : LETTER (LETTER | DIGIT)* ;

fragment DIGIT  : [0-9] ;
fragment LETTER : [a-zA-Z_] ;
