lexer grammar UnibashLexer;

NEWLINE
    : '\r'? '\n'
    ;
WS
    : [ \t]+ -> skip
    ;
COMMENT
    : '#' ~[\r\n]* -> skip
    ;

PIPE      : '|';
SEMI      : ';';
REDIR_OUT : '>';
REDIR_IN  : '<';
REDIR_APP : '>>';

SQUOTE_STRING
    : '\'' ( '\'\'' | ~'\'' )* '\''
    ;
DQUOTE_STRING
    : '"' ( '\\"' | '\\' . | ~["\\] )* '"'
    ;
WORD
    : ~[ \t\r\n;|<>`"']+
    ;
