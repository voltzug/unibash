parser grammar UnibashParser;
options { tokenVocab=UnibashLexer; }

// #0. Program structure
program
    : sep* (statement (sep+ statement)*)? sep* EOF
    ;

sep
    : SEMI NEWLINE
    | NEWLINE
    | SEMI
    ;

block
    : LBRACE sep* (statement (sep+ statement)*)? sep* RBRACE
    ;

// #0. Statements
statement
    : host_decl
    | range_decl
    | group_decl
    | set_stmt
    | ping_stmt
    | connect_stmt
    | inspect_stmt
    | process_stmt
    | download_stmt
    | upload_stmt
    | copy_stmt
    | ip_config_stmt
    | dhcp_config
    | dns_config
    | http_stmt
    | exec_stmt
    | print_stmt
    | if_stmt
    | foreach_stmt
    | on_block
    | via_block
    ;

// #1. Host definitions
host_decl
    : HOST IDENT ASSIGN (addr | string_literal) host_option*
    ;

host_option
    : VIA (protocol | name)
    | PORT NUMBER
    | USER name
    | PASSWORD name
    | KEY name
    ;

protocol
    : SSH
    | TELNET
    ;

// #2. Ranges and groups
range_decl
    : RANGE IDENT ASSIGN range_expr
    ;

range_expr
    : value DOTDOT value
    | list_literal
    ;

group_decl
    : GROUP IDENT ASSIGN list_literal
    ;

// #3. Variables
set_stmt
    : SET IDENT ASSIGN value
    ;

// #4. Ping diagnostics
ping_stmt
    : PING target (COUNT NUMBER)? (TIMEOUT (IDENT | NUMBER))?
    ;

// #5. Interactive connect
connect_stmt
    : CONNECT target
    ;

// #6. System inspection
inspect_stmt
    : INSPECT target (SHOW inspect_category)?
    ;

inspect_category
    : OS
    | MEMORY
    | DISK
    | CPU
    | NETWORK
    | value // ? too exhausive
    ;

// #7. Process management
process_stmt
    : (RESTART | STOP | START | STATUS) (PROCESS value)? (ON target | target)?
    ;

// #8. File operations
download_stmt
    : DOWNLOAD name FROM target TO name
    ;

upload_stmt
    : UPLOAD name TO target PATH name
    ;

copy_stmt
    : COPY name FROM target TO target PATH name
    ;

// #9. IP configuration
ip_config_stmt
    : (SET | ADD) IP value ON target INTERFACE value
    ;

// #10. DHCP configuration
dhcp_config
    : CONFIGURE DHCP ON target dhcp_block
    ;

dhcp_block
    : LBRACE sep* dhcp_entry (sep+ dhcp_entry)* sep* RBRACE
    ;

dhcp_entry
    : SUBNET value
    | RANGE range_expr
    | GATEWAY value
    | DNS list_literal
    ;

// #11. DNS configuration
dns_config
    : CONFIGURE DNS ON target dns_block
    ;

dns_block
    : LBRACE sep* dns_entry (sep+ dns_entry)* sep* RBRACE
    ;

dns_entry
    : ZONE value
    | RECORD value value value?
    | FORWARDERS list_literal
    ;

// #12. Conditions (if / else)
if_stmt
    : IF condition block (ELSE IF condition block)* (ELSE block)?
    ;

// #13. Loops (foreach)
foreach_stmt
    : FOREACH IDENT IN target (WHERE foreach_condition)? block
    ;

foreach_condition
    : foreach_operand (EQ | NEQ) foreach_operand
    ;

foreach_operand
    : OS target?
    | value
    ;

// #14. Remote execution (on)
on_block
    : ON target block
    ;

// #15. Remote execution (via)
via_block
    : VIA target RUN block
    ;

// #16. HTTP requests
http_stmt
    : HTTP http_method value (SAVE value)? http_block?
    ;

http_method
    : GET
    | POST
    | PUT
    | DELETE
    | PATCH
    | HEAD
    ;

http_block
    : LBRACE sep* http_entry (sep+ http_entry)* sep* RBRACE
    ;

http_entry
    : HEADER value value
    | BODY value
    ;

// #17. Exec blocks
exec_stmt
    : EXEC ON target (value | exec_block)
    ;

exec_block
    : LBRACE sep* exec_line (sep+ exec_line)* sep* RBRACE
    ;

exec_line : string_literal ;

// #18. Printing
print_stmt
    : PRINT (inspect_stmt | value+)
    ;

// #19. Conditions and operands
condition
    : operand (EQ | NEQ) operand
    ;

operand
    : OS target
    | value
    ;

// #0. Common refs
target
    : RANGE IDENT
    | GROUP IDENT
    | IDENT
    ;

name
    : IDENT
    | string_literal
    ;
addr
    : IP4ADDR
    | IP6ADDR
    ;
value
    : NUMBER
    | addr
    | name
    ;

string_literal
    : SQUOTE_STRING
    | DQUOTE_STRING
    ;

// #0. Lists
list_literal
    : LBRACK (value (COMMA value)*)? RBRACK
    ;
