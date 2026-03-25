parser grammar UnibashParser;

options { tokenVocab=UnibashLexer; }

program
  : statement* EOF
  ;

statement
  : pipeline terminator*
  | terminator+
  ;

terminator
  : SEMI
  | NEWLINE
  ;

pipeline
  : command (PIPE command)*
  ;

command
  : argument+ redirect*
  | redirect+
  ;

argument
  : WORD
  | SQUOTE_STRING
  | DQUOTE_STRING
  ;

redirect
  : REDIR_IN argument
  | REDIR_OUT argument
  | REDIR_APP argument
  ;
