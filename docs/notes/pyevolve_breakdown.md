# PyEvolve - important notes that summarize what it does and how

## Workflow

!['PyEvolve workflow'](/PyEvolve/workflow.jpg)

## Motivation - why is the tool exceptional

- introduces a new “Transformation by Example” technique
- "data- and control-flow aware"
  - so if the same thing is implemented differently, it recognises it, and it can adapt the transformation rule(?)
  - semantically-equivalent but syntactically-different
  - ex:
!['table'](/docs/notes/infer_rule_table.PNG)

## How does it do it? - workflow breakdown

- TODO

## Running the app as a black box

**CLI app**:

### pycraft infer [PARAMS]

*Infer transformation rules for a given set of patterns*

**"-p", "--patterns"** => "Path for the pattern repository"

**"-r", "--rules"** => "Output path for the transformation rule repository"

Patterns: the CPATs (CVE fixes) collected into a specific file format.
It makes rules out of them, and puts them into to rules directory.

### pycraft transform [PARAMS]

*Apply transformations defied in the rules to code bases*

**"-r","--repositories"** => "Path for project repository"

**"-t","--types"** => "Path for type repository"

**"-f","--files"** => "The text file contains the file paths of Python files that need to be refactored."

**"-p","patterns"** => "Path for code patterns"

Project and type repos: what are those???

A másik kettő adja magát tbh.
