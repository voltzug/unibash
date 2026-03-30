parser grammar UnibashParser;

options { tokenVocab=UnibashLexer; }

// #0. Program structure
program
  : statement* EOF
  ;

statement
  : host_decl terminator*
  | range_decl terminator*
  | group_decl terminator*
  | set_stmt terminator*
  | ping_stmt terminator*
  | connect_stmt terminator*
  | inspect_stmt terminator*
  | process_stmt terminator*
  | download_stmt terminator*
  | upload_stmt terminator*
  | copy_stmt terminator*
  | ip_config_stmt terminator*
  | dhcp_config terminator*
  | dns_config terminator*
  | http_stmt terminator*
  | exec_stmt terminator*
  | print_stmt terminator*
  | if_stmt
  | foreach_stmt
  | on_block
  | via_block
  | terminator+
  ;

terminator
  : SEMI
  | NEWLINE
  ;

// #1. Host definitions
host_decl
  : HOST name ASSIGN value host_option*
  ;

host_option
  : VIA value
  | PORT NUMBER
  | USER value
  | PASSWORD value
  | KEY value
  ;

// #2. Ranges and groups
range_decl
  : RANGE name ASSIGN range_expr
  ;

range_expr
  : value DOTDOT value
  | list_literal
  ;

group_decl
  : GROUP name ASSIGN list_literal
  ;

// #3. Variables
set_stmt
  : SET name ASSIGN value
  ;

// #4. Ping diagnostics
ping_stmt
  : PING target (COUNT NUMBER)? (TIMEOUT value)?
  ;

// #5. Interactive connect
connect_stmt
  : CONNECT target
  ;

// #6. System inspection
inspect_stmt
  : INSPECT target (SHOW value)?
  ;

// #7. Process management
process_stmt
  : PROCESS (RESTART | STOP | START | STATUS) (PROCESS value)? (ON target)?
  | (RESTART | STOP | START | STATUS) (PROCESS value)? (ON target)?
  ;

// #8. File operations
download_stmt
  : DOWNLOAD value FROM target TO value
  ;

upload_stmt
  : UPLOAD value TO target PATH value
  ;

copy_stmt
  : COPY value FROM target TO target PATH value
  ;

// #9. IP configuration
ip_config_stmt
  : (SET | ADD) IP value ON target INTERFACE value
  ;

// #10. DHCP configuration
dhcp_config
  : CONFIGURE DHCP ON target block
  ;

dhcp_entry
  : SUBNET value
  | RANGE range_expr
  | GATEWAY value
  | DNS list_literal
  ;

// #11. DNS configuration
dns_config
  : CONFIGURE DNS ON target block
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
  : FOREACH name IN source (WHERE condition)? block
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
  : LBRACE (terminator* http_entry terminator*)* RBRACE
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
  : LBRACE (terminator* exec_line terminator*)* RBRACE
  ;

exec_line
  : value+
  ;

// #18. Printing
print_stmt
  : PRINT (inspect_stmt | value+)
  ;

// #19. Generic block body
block
  : LBRACE block_item* RBRACE
  ;

block_item
  : dhcp_entry terminator*
  | dns_entry terminator*
  | statement
  ;

// #0. Conditions and operands
condition
  : operand (EQ | NEQ) operand
  ;

operand
  : OS target?
  | value
  ;

// #0. Common refs
source
  : RANGE name
  | GROUP name
  | name
  ;

name
  : WORD
  ;

target
  : RANGE name
  | GROUP name
  | name
  ;

value
  : WORD
  | NUMBER
  | IPADDR
  | string_literal
  ;

string_literal
  : SQUOTE_STRING
  | DQUOTE_STRING
  ;

// #0. Lists
list_literal
  : LBRACK (value (COMMA value)*)? RBRACK
  ;
