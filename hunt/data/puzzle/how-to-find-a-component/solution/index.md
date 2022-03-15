Each of the 9 feeder answers must be converted to its alphabetically-ordered numbering (i.e., the letter of the answer that occurs first alphabetically is assigned the digit 1, the letter that occurs second alphabetically is assigned the digit 2, and so on up to 9).

The nine 9-digit strings thus formed will be (in alphabetical order):

```
1	2	6	8	9	3	4	5	7		DIRTY MOPS

3	7	2	9	1	5	6	8	4		FLETCHING

2	6	9	7	8	4	3	1	5		FOURTH GEN

4	1	5	3	2	6	9	7	8		HALF-COURT

6	5	7	4	3	8	2	9	1		KING COBRA

7	9	8	5	4	2	1	3	6		LURED BACK

5	3	4	1	6	7	8	2	9		MEGASTUDY

8	4	1	2	7	9	5	6	3		SHADOWING

9	8	3	6	5	1	7	4	2		ZYGOMATIC
```

These 9-digit strings must be entered into the rows of a KenKen or calcudoku grid that is gradually revealed to solvers as they gather more feeder answers.  Some of the cages in the grid contain the target number and the operator, but some are missing the target number.

Solvers must calculate the target number of each cage where one is not provided, then use that number as an alphabet index, reading through the grid in row-major order, leading to the final answer:  <span class="answer">STEP BY STEP LADDER</span>.

![](solvedgrid.png)
