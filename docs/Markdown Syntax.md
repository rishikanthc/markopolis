---
publish: true
tags:
- syntax
- markdown
title: Markdown Syntax
---
# Headings

```markdown
# Heading 1
## Heading 2
### Heading 3
#### Heading 4
##### Heading 5
```


# Heading 1
## Heading 2
### Heading 3
#### Heading 4
##### Heading 5

## Horizontal line

---

## Tags

```markdown
#tag1 #tag2 #tag3
```

#tag1 #tag2 #tag3

## Images

### embed images
Image names should be unique. Duplicate images will be overwritten.

```markdown
![[image.png]]

![](image.png)
```

![[image.png]]

![](image.png)

### external images

```markdown
![Engelbart](https://history-computer.com/ModernComputer/Basis/images/Engelbart.jpg)
```

![Engelbart](https://history-computer.com/ModernComputer/Basis/images/Engelbart.jpg)

## Wikilinks

```markdown
[[Installation]]
[[f1/test]]
[[f2/test]]
```

[[installation]]
[[f1/test]]
[[f2/test]]

## Text formatting
```markdown
**Bold text**
*Italic text*
~~this puts a strikethrough~~
==this highlights text==
**Bold text and _nested italic_ text**
***Bold and italic text***
```

**Bold text**
*Italic text*
~~this puts a strikethrough~~
==this highlights text==
**Bold text and _nested italic_ text**
***Bold and italic text***

## Equations

```markdown
$$
\sum_i = x
$$
```

$$
\sum_i = x
$$

## Footnotes

```markdown
This is a simple footnote[^1].


[^1]: This is the referenced text.
[^2]: Add 2 spaces at the start of each new line.
  This lets you write footnotes that span multiple lines.
[^note]: Named footnotes still appear as numbers, but can make it easier to identify and link references.
```

This is a simple footnote[^1].


## Quotes

```markdown
> Human beings face ever more complex and urgent problems, and their effectiveness in dealing with these problems is a matter that is critical to the stability and continued progress of society.

\- Doug Engelbart, 1961
```

> Human beings face ever more complex and urgent problems, and their effectiveness in dealing with these problems is a matter that is critical to the stability and continued progress of society.

\- Doug Engelbart, 1961

## Tables

```markdown
| First name | Last name |
| ---------- | --------- |
| Max        | Planck    |
| Marie      | Curie     |
```

| First name | Last name |
| ---------- | --------- |
| Max        | Planck    |
| Marie      | Curie     |

The vertical bars on either side of the table are optional.

Cells don't need to be perfectly aligned with the columns. Each header row must have at least two hyphens.

```markdown
First name | Last name
-- | --
Max | Planck
Marie | Curie
```

First name | Last name
-- | --
Max | Planck
Marie | Curie

## Mermaid diagrams

Some text.

```mermaid
graph TB
A --> B
B --> C
```

```mermaid
flowchart LR



A[Osaka 7-8] --> B[Tokyo 9-11]
B -.Nagano .-> C[Matsumoto]
C -.Nagano & Toyama.-> D[Takayama 12] <--> D1(Hida no Sato village)
B -.Nagano & Toyama.-> D
C <-.bus.-> D
D --Toyama---> E <--> D2([Onsen 14]) --> F
E[Kanazawa 13] ---> F[Kyoto 15-18] <--> F2(Uji) <--> F1(Nara)
F <-.-> F4(Himeji)
```

### Large chart

```mermaid
timeline
    section .NET Framework
        2000 - 2005
             : .NET Framework 1.0
             : .NET Framework 1.0 SP1
             : .NET Framework 1.0 SP2
             : .NET Framework 1.1
             : .NET Framework 1.0 SP3
             : .NET Framework 2.0
        2006 - 2009
             : .NET Framework 3.0
             : .NET Framework 3.5
             : .NET Framework 2.0 SP 1
             : .NET Framework 3.0 SP 1
             : .NET Framework 2.0 SP 2
             : .NET Framework 3.0 SP 2
             : .NET Framework 3.5 SP 1
        2010 - 2015
             : .NET Framework 4.0
             : .NET Framework 4.5
             : .NET Framework 4.5.1
             : .NET Framework 4.5.2
             : .NET Framework 4.6
             : .NET Framework 4.6.1
    section .NET Core
        2016 - 2017
             : .NET Core 1.0
             : .NET Core 1.1
             : .NET Framework 4.6.2
             : .NET Core 2.0
             : .NET Framework 4.7
             : .NET Framework 4.7.1
        2018 - 2019
             : .NET Core 2.1
             : .NET Core 2.2
             : .NET Framework 4.7.2
             : .NET Core 3.0
             : .NET Core 3.1
             : .NET Framework 4.8
    section Modern .NET
        2020 : .NET 5
        2021 : .NET 6
        2022 : .NET 7
             : .NET Framework 4.8.1

```

## Callouts

> [!abstract]
> Lorem ipsum dolor sit amet

> [!info]
> Lorem ipsum dolor sit amet

> [!todo]
> Lorem ipsum dolor sit amet

> [!tip]
> Lorem ipsum dolor sit amet

> [!success]
> Lorem ipsum dolor sit amet

> [!question]
> Lorem ipsum dolor sit amet

> [!warning]
> Lorem ipsum dolor sit amet

> [!failure]
> Lorem ipsum dolor sit amet

> [!danger]
> Lorem ipsum dolor sit amet

> [!bug]
> Lorem ipsum dolor sit amet

> [!example]
> Lorem ipsum dolor sit amet

> [!quote]
> Lorem ipsum dolor sit amet

> [!tip] Title-only callout

[^1]: This is the referenced text.
[^2]: Add 2 spaces at the start of each new line.
  This lets you write footnotes that span multiple lines.
[^note]: Named footnotes still appear as numbers, but can make it easier to identify and link references.
