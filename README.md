# The Mail and Globe

## About

These scripts power the [@mailandglobe](http://www.twitter.com/mailandglobe) Twitter feed, a satircal twist on the [@globeandmail](http://www.twitter.com/globeandmail).

In particular, @mailandglobe tweets frankenstein versions of @globeandmail tweets.

Frankenstein grammar:

            Prep  ->  as | of | on | in | if | at | to | and
         Tweet_1  ->  A_1 Prep B_1 | Tweet_1
         Tweet_2  ->  A_2 Prep B_2 | Tweet_2
         ...
         Tweet_N  ->  A_N Prep B_N | Tweet_N
    Frankenstein  ->  A_i Prep B_j | Tweet_i Prep B_j

In English: Given a database of N tweets, a frankenstein tweet is

1. a tweet joined using a preposition from two half-tweets in the database broken apart by the same preposition; or
2. a full tweet from the database, followed by a preposition and a half-tweet from the database that begins with the same preposition.

## How it works

tbc

## Installation

tbc
