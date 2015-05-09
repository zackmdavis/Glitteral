## the Glitteral programming language 

### (in speculative pre-development)

*sparkling, vague dreams of a future programming language*

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
(defλ name "docstring" positional-args keyword-args body)

# Both underscores and hyphens are legal in identifier names, but
# (contrary to what patriotic fools will tell you is essential to
# Lisp-likeness) _underscores_ are strongly encouraged except where you
# would actually use a hyphen when writing English.

(defλ my_super-great_function
      "This is my function."
      |foo :int bar :float| {quux :boolean;}
  (let |foo_times_two (⋅ 2 foo)
        quux_of_bar (quux bar)|
     (÷ foo_times_two quux_of_bar)))

# global variable declaration
(def foo :int 3)

# instead of Lisp-like "apply", we have Python-like "positional glitter"—

(def my_numbers :[int] |1 2 3|)

(defλ add_three_numbers [a b c] <>
  (+ a b c))

(add_three_numbers *my_numbers)  # => 6

# and "associative glitter"—

(my_function_with_kwargs **<'foo' "bar"; 'quux' 2;>)

```

#### About the name

A *portmanteau* of *glitter* and *literal*, because things that sparkle are OK and one of the things that I like about Clojure (over *e.g.* Scheme) is how there's a rich "literal" syntax for things like lists and hashtables which is easier to read than *all* delimiters being parentheses, and I like literacy, and *portmanteau*s.

The name isn't Google-unique: for example, we can find an [abandoned DeviantArt account](http://glitteral.deviantart.com/), an [Instagram user](https://instagram.com/glitteral/), and a [recording by](https://www.youtube.com/watch?v=_WdRaT94rio) a musical artist called Eagles for Hands with the same identifier, but the world is big enough and short, memorable names are [scarce enough](http://en.wikipedia.org/wiki/Information_theory) that maybe not everything needs to be unique, and no one will mind.