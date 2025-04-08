# Python implementation of Neil Larson's DOS based PERM Decision Tree Builder

Perm was a DOS program written by Neil Larson to convert three hierarchical input files into a decision tree or search tree. The input files are as follows:

Attribute File
Category File
Priority File

Larson used his MaxThink outliner to create the input files, but any ASCII text editor can be pressed into service as long as leading spaces or tabs are used to indicate the different levels of the outline. If using leading tabs, and MaxThink compatibility is desired, the Linux expand command may be used to convert the file back into MaxThink mode as follows:

cat a.otl | expand --tabs=1 > a.mt
The Linux unexpand command may be used to convert a MaxThink file into one using leading tabs as follows:

cat a.mt | unexpand --tabs=1 > a.otl

## ATTRIBUTE FILE (A)
A simple decision tree to select a beverage would use an attribute file as follows:

```
TITLE
 DRINK COKE
  COLOR: BROWN
  COST: 75 CENTS
  TASTE: TART
 DRINK PEPSI
  TASTE: TART
  COLOR: BROWN
  COST: 80 CENTS
 DRINK ROOT BEER
  COLOR: TAN
  COST: 75 CENTS
  TASTE: SWEET
```
  
Attribute tags (COLOR, COST, TASTE) are optional, but the files must be consistent.

## CATEGORY FILE (B)
The second file which is derived from the Attribute File and has the following structure:

```
TITLE
 WHAT IS THE PRICE?
  COST: 75 CENTS
  COST: 80 CENTS
 WHAT IS THE COLOR?
  COLOR: BROWN
  COLOR: TAN
 WHAT IS THE TASTE?
  TASTE: SWEET
  TASTE: TART
```

## PRIORITY FILE (C)
The third file which is derived from the Category File is as follows:

```
Drink Decision Tree
 PRICE BUYER
  WHAT IS THE PRICE?
  WHAT IS THE COLOR?
  WHAT IS THE TASTE?
 COLOR BUYER
  WHAT IS THE COLOR?
  WHAT IS THE TASTE?
  WHAT IS THE PRICE?
 TASTE BUYER
  WHAT IS THE TASTE?
  WHAT IS THE COLOR?
  WHAT IS THE PRICE?
```

## OUTPUT FILE (D)

Typing "perm A B C > D" from the command prompt should create Output File D with minimal paths to the recommended actions.

```
Drink Decision Tree
 PRICE BUYER
  COST: 75 CENTS
   TASTE: TART
    DRINK COKE
   TASTE: SWEET
    DRINK ROOT BEER
  COST: 80 CENTS
   DRINK PEPSI
 COLOR BUYER
  COLOR: BROWN
   COST: 75 CENTS
    DRINK COKE
   COST: 80 CENTS
    DRINK PEPSI
   COLOR: TAN
    DRINK ROOT BEER
 TASTE BUYER
  TASTE: SWEET
   DRINK ROOT BEER
  TASTE: TART
   COST: 75 CENTS
    DRINK COKE
   COST: 80 CENTS
    DRINK PEPSI
```
