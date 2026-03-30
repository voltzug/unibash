parser grammar UnibashParser;

options { tokenVocab = UnibashLexer; }

program
    : sep* (statement (sep+ statement)*)? sep* EOF
    ;

sep
    : NEWLINE
    | SEMI
    ;

block
    : LBRACE sep* (statement (sep+ statement)*)? sep* RBRACE
    ;

statement
    : hostDef
    | rangeDef
    | groupDef
    | pingCmd
    | connectCmd
    | restartCmd
    | stopCmd
    | startCmd
    | statusCmd
    | downloadCmd
    | uploadCmd
    | copyCmd
    | inspectCmd
    | setIpCmd
    | addIpCmd
    | configureDhcp
    | configureDns
    | ifBlock
    | foreachBlock
    | onBlock
    | viaBlock
    | httpCmd
    | execCmd
    | printCmd
    | varAssign
    ;

hostDef
    : HOST IDENT ASSIGN stringLiteral hostOption*
    ;

hostOption
    : VIA protocol
    | PORT NUMBER
    | USER stringLiteral
    | PASSWORD stringLiteral
    | KEY stringLiteral
    ;

protocol
    : SSH
    | TELNET
    ;

rangeDef
    : RANGE IDENT ASSIGN rangeValue
    ;

rangeValue
    : ipRange
    | list
    ;

ipRange
    : IP_ADDR DOT_DOT IP_ADDR
    ;

groupDef
    : GROUP IDENT ASSIGN list
    ;

list
    : LBRACKET listItem (COMMA listItem)* RBRACKET
    ;

listItem
    : IDENT
    | stringLiteral
    ;

target
    : RANGE IDENT
    | IDENT
    ;


pingCmd
    : PING target (COUNT NUMBER)? (TIMEOUT NUMBER)?
    ;

connectCmd
    : CONNECT target
    ;

restartCmd
    : RESTART PROCESS stringLiteral ON target
    | RESTART target
    ;

stopCmd
    : STOP PROCESS stringLiteral ON target
    ;

startCmd
    : START PROCESS stringLiteral ON target
    ;

statusCmd
    : STATUS PROCESS stringLiteral ON target
    ;


downloadCmd
    : DOWNLOAD stringOrIdent FROM target TO stringLiteral
    ;

uploadCmd
    : UPLOAD stringOrIdent TO target PATH stringLiteral
    ;

copyCmd
    : COPY stringOrIdent FROM target TO target PATH stringLiteral
    ;

stringOrIdent
    : stringLiteral
    | IDENT
    ;

inspectCmd
    : INSPECT target (SHOW inspectCategory)?
    ;

inspectCategory
    : OS
    | MEMORY
    | DISK
    | CPU
    | NETWORK
    ;

setIpCmd
    : SET IP stringLiteral ON target INTERFACE stringLiteral
    ;

addIpCmd
    : ADD IP stringLiteral ON target INTERFACE stringLiteral
    ;

configureDhcp
    : CONFIGURE DHCP ON target LBRACE sep* dhcpOption (sep+ dhcpOption)* sep* RBRACE
    ;

dhcpOption
    : SUBNET stringLiteral
    | RANGE ipRange
    | GATEWAY stringLiteral
    | DNS list
    ;

configureDns
    : CONFIGURE DNS ON target LBRACE sep* dnsOption (sep+ dnsOption)* sep* RBRACE
    ;

dnsOption
    : ZONE stringLiteral
    | RECORD IDENT stringLiteral stringLiteral
    | FORWARDERS list
    ;

ifBlock
    : IF condition block elseIfBlock* elseBlock?
    ;

elseIfBlock
    : ELSE IF condition block
    ;

elseBlock
    : ELSE block
    ;

condition
    : condLeft compareOp condRight
    ;

condLeft
    : OS target
    | OS
    | IDENT
    ;

compareOp
    : EQUALS
    | NOT_EQ
    ;

condRight
    : stringLiteral
    | NUMBER
    | IDENT
    ;

foreachBlock
    : FOREACH IDENT IN target (WHERE condition)? block
    ;

onBlock
    : ON target block
    ;

viaBlock
    : VIA target RUN block
    ;

httpCmd
    : HTTP httpMethod stringLiteral httpBody? (SAVE stringLiteral)?
    ;

httpMethod
    : GET
    | POST
    | PUT
    | DELETE
    | PATCH
    ;

httpBody
    : LBRACE sep* httpOption (sep+ httpOption)* sep* RBRACE
    ;

httpOption
    : HEADER stringLiteral stringLiteral
    | BODY stringLiteral
    ;

execCmd
    : EXEC ON target stringLiteral
    | EXEC ON target execBlock
    ;

execBlock
    : LBRACE sep* stringLiteral (sep+ stringLiteral)* sep* RBRACE
    ;

printCmd
    : PRINT stringLiteral
    | PRINT inspectCmd
    ;

varAssign
    : SET IDENT ASSIGN value
    ;

value
    : stringLiteral
    | NUMBER
    | IP_ADDR
    ;

stringLiteral
    : SQUOTE_STR
    | DQUOTE_STR
    ;
