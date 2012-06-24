" Vim syntax file
" Language: wheezy template
" Maintainer: Andriy Kornatskyy
" Latest Revision: 2 June 2012

" Matches
syn match wComment '^\s*#.*$'
syn match wComment '@#.*$'
syn match wBlock '\s*@($'
syn match wBlock '^\s*)$'
syn match wBlock '@(.*)'
syn match wVar '\(@\)\@<!@[a-z\.]\+'
syn match wStmt ':$'
syn match wStmt '\(@\)\@<!@\(def\|for\|if\|elif\|else\|end\|require\|extends\|include\|from\|import\)'



hi def link wComment    Comment
hi def link wBlock      PreProc
hi def link wStmt       Statement
hi def link wVar        Special
