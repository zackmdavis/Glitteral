## the Glitteral programming language 

#### (in speculative pre-development)

*sparkling, vague dreams of a future programming language*

### Actual demonstration

```
$ cat demo.gltrl
(:= glitteral_is_splendid Truth)

(:=λ first_plus_square_of_second |a ^int b ^int| → ^int
  (+ a (⋅ b b)))  # This is a comment.

(:= my_list [1 2 3])
(append! my_list 4)

(if glitteral_is_splendid
  (if (= (first_plus_square_of_second 1 2) 5)
    (_:= my_list 0 10)
    (print_integer 0))
  (print_integer 0))

(for |i my_list|
  (print_integer i))
$ ./glitteralc demo.gltrl 
$ ./demo 
10
2
3
4
```

#### "design document" (daydreaming)

```
# comment

'foo' # intern
"foo" # string

# Sequentials
["foo" "bar" "quux"]  # list (mutable) 
|"foo" "bar" "quux"|  # vector (immutable) 

# Mappings
{'foo' 1; 'bar' 2; 'quux' 3;}  # dictionary (mutable) 
<'foo' 1; 'bar' 2; 'quux' 3;>  # hashtable (immutable) 

# if the second part of a mapping entry isn't present, it defaults to Truth
# it's idiomatic to represent sets as Mappings of one-item entries

# booleans
Truth Falsity

# null
Void

(+ 1 2)  # addition
(− 2 1)  # subtraction (that's a Unicodepoint 2212 minus sign)
(⋅ 2 3)  # multiplication (Unicodepoint 22C5 dot operator)
(÷ 2 3)  # division (Unicodepoint 00F7)

# type annotation names?
# [] || {} <> int float str intern boolean codeform symbol

# regex literals??
/fooo*/ /barr?/

# anonymous functions
(λ positional-args keyword-args body)

# named function definitions
(:=λ name "docstring" positional-args keyword-args body)

# Both underscores and hyphens are legal in identifier names, but
# (contrary to what patriotic fools will tell you is essential to
# Lisp-likeness) _underscores_ are strongly encouraged except where you
# would actually use a hyphen when writing English.

(:=λ my_super-great_function
      "This is my function."
      |foo ^int bar ^float| → ^float
  (let |foo_times_two (⋅ 2 foo)
        quux_of_bar (quux bar)|
     (÷ foo_times_two quux_of_bar)))

# global variable declaration
(:= foo ^int 3)

# instead of Lisp-like "apply", we have Python-like "positional glitter"—

(:= my_numbers ^[int] |1 2 3|)

(:=λ add_three_numbers [a b c] <>
  (+ a b c))

(add_three_numbers *my_numbers)  # => 6

# and "associative glitter"—

(my_function_with_kwargs **<'foo' "bar"; 'quux' 2;>)

```

#### About the name

A *portmanteau* of *glitter* and *literal*, because things that sparkle are OK and one of the things that I like about Clojure (over *e.g.* Scheme) is how there's a rich "literal" syntax for things like lists and hashtables, which is easier to read than *all* delimiters being parentheses. Also, I like literacy (and *portmanteau*s).

The name isn't Google-unique: other things with the same name include an [abandoned DeviantArt account](http://glitteral.deviantart.com/), an [Instagram user](https://instagram.com/glitteral/), and a [recording by](https://www.youtube.com/watch?v=_WdRaT94rio) a musical artist called Eagles for Hands. But the world is big enough and short, memorable names are [scarce enough](http://en.wikipedia.org/wiki/Information_theory) that maybe not everything needs to be unique, and no one will mind.
