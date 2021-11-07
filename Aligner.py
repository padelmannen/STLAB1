from __future__ import print_function
import argparse
import codecs
import random

import numpy as np
import json
import requests

"""
This file is part of the computer assignments for the course DD1418/DD2418 Language engineering at KTH.
Created 2017 by Johan Boye and Patrik Jonell.
"""

"""
This module computes the minimum-cost alignment of two strings.
"""

"""
When printing the results, only print BREAKOFF characters per line.
"""
BREAKOFF = 60


def compute_backpointers(s0, s1):
    """
    <p>Computes and returns the backpointer array (see Jurafsky and Martin, Fig 3.27)
    arising from the calculation of the minimal edit distance of two strings
    <code>s0</code> and <code>s1</code>.</p>

    <p>The backpointer array has three dimensions. The first two are the row and
    column indices of the table in Fig 3.27. The third dimension either has
    the value 0 (in which case the value is the row index of the cell the backpointer
    is pointing to), or the value 1 (the value is the column index). For example, if
    the backpointer from cell (5,5) is to cell (5,4), then
    <code>backptr[5][5][0]=5</code> and <code>backptr[5][5][1]=4</code>.</p>

    :param s0: The first string.
    :param s1: The second string.
    :return: The backpointer array.
    """
    if s0 == None or s1 == None:
        raise Exception('Both s0 and s1 have to be set')
    # s0 är lodrätt

    backptr = [[[0, 0] for y in range(len(s1) + 1)] for x in range(len(s0) + 1)]

    matrix = np.zeros((len(s0) + 1, len(s1) + 1))
    matrix[0] = [j for j in range(len(s1) + 1)]
    matrix[:, 0] = [j for j in range(len(s0) + 1)]
    print(matrix)

    for row in range(1, len(s0) + 1):
        for col in range(1, len(s1) + 1):

            minimum = min(matrix[row - 1, col] + 1,
                          matrix[row, col - 1] + 1,
                          matrix[row - 1, col - 1] + subst_cost(s0[row - 1], s1[col - 1])
                          )
            matrix[row, col] = minimum

            leftCost = matrix[row, col - 1] + 1
            downCost = matrix[row - 1, col] + 1
            diagCost = matrix[row - 1, col - 1] + subst_cost(s0[row - 1], s1[col - 1])
            #
            #
            # if matrix[row - 1, col - 1] + subst_cost(s0[row - 1], s1[col - 1]) == minimum:
            #     x = row - 1
            #     y = col - 1
            #
            # elif matrix[row, col - 1] + 1 == minimum:
            #     x = row
            #     y = col - 1
            #
            # else:
            #     x = row - 1
            #     y = col

            if ((leftCost < downCost) and (leftCost < diagCost)):
                # We should come from the left in our backtrace matrix
                #matrix[i][j][0] = leftCost
                backptr[row][col][0], backptr[row][col][1] = row, col-1
            elif ((downCost <= leftCost) and (downCost < diagCost)):
                # We should come from below
                #matrix[i][j][0] = downCost
                backptr[row][col][0], backptr[row][col][1] = row-1, col
            elif ((diagCost <= leftCost) and (diagCost <= downCost)):
                # We should come from diagonally behind
                #matrix[i][j][0] = diagCost
                backptr[row][col][0], backptr[row][col][1] = row-1, col-1

            # backptr[row][col][0] = x
            # backptr[row][col][1] = y


    print(matrix)
        #print(backptr)
    return backptr


def subst_cost(c0, c1):
    """
    The cost of a substitution is 2 if the characters are different
    or 0 otherwise (when, in fact, there is no substitution).
    """
    return 0 if c0 == c1 else 2


def align(s0, s1, backptr):
    """
    <p>Finds the best alignment of two different strings <code>s0</code>
    and <code>s1</code>, given an array of backpointers.</p>

    <p>The alignment is made by padding the input strings with spaces. If, for
    instance, the strings are <code>around</code> and <code>rounded</code>,
    then the padded strings should be <code>around  </code> and
    <code> rounded</code>.</p>

    :param s0: The first string.
    :param s1: The second string.
    :param backptr: A three-dimensional matrix of backpointers, as returned by
    the <code>diff</code> method above.
    :return: An array containing exactly two strings. The first string (index 0
    in the array) contains the string <code>s0</code> padded with spaces
    as described above, the second string (index 1 in the array) contains
    the string <code>s1</code> padded with spaces.
    """
    result = ['', '']
    i0 = len(s0)
    j0 = len(s1)
    # (i0, j0) gives us top right corner of backptr matrix

    while True:
        i, j = backptr[i0][j0][0], backptr[i0][j0][1]

        if ((i0 - 1 == i) and (j0 - 1 == j)):
            # Then, this is a diagonal move.
            result[0] += s0[i0 - 1]
            result[1] += s1[j0 - 1]
        elif (j0 - 1 == j):
            # This is a move from the left
            result[0] += ' '
            result[1] += s1[j0 - 1]
        elif (i0 - 1 == i):
            # This is a move from below
            result[0] += s0[i0 - 1]
            result[1] += ' '

        i0, j0 = i, j

        if ((i0 == 0) and (j0 == 0)):
            # We have reached index (0, 0) in the backptr matrix.
            break

    # print(backptr)

    return result


def print_alignment(s):
    """
    <p>Prints two aligned strings (= strings padded with spaces).
    Note that this printing method assumes that the padded strings
    are in the reverse order, compared to the original strings
    (because we are following backpointers from the end of the
    original strings).</p>

    :param s: An array of two equally long strings, representing
    the alignment of the two original strings.
    """
    if s[0] == None or s[1] == None:
        return None
    start_index = len(s[0]) - 1
    while start_index > 0:
        end_index = max(0, start_index - BREAKOFF + 1)
        print_list = ['', '', '']
        for i in range(start_index, end_index - 1, -1):
            print_list[0] += s[0][i]
            print_list[1] += '|' if s[0][i] == s[1][i] else ' '
            print_list[2] += s[1][i]

        for x in print_list: print(x)
        start_index -= BREAKOFF


def main():
    """
    Parse command line arguments
    """
    parser = argparse.ArgumentParser(description='Aligner')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--file', '-f', type=str, nargs=2, help='align two strings')
    group.add_argument('--string', '-s', type=str, nargs=2, help='align the contents of two files')

    parser.add_argument('--check', action='store_true', help='check if your alignment is correct')

    arguments = parser.parse_args()

    if arguments.file:
        f1, f2 = arguments.file
        with codecs.open(f1, 'r', 'utf-8') as f:
            s1 = f.read().replace('\n', '')
        with codecs.open(f2, 'r', 'utf-8') as f:
            s2 = f.read().replace('\n', '')

    elif arguments.string:
        s1, s2 = arguments.string

    if arguments.check:
        payload = json.dumps({
            's1': s1,
            's2': s2,
            'result': align(s1, s2, compute_backpointers(s1, s2))
        })
        response = requests.post(
            'https://language-engineering.herokuapp.com/correct',
            data=payload,
            headers={'content-type': 'application/json'}
        )
        response_data = response.json()
        if response_data['correct']:
            print_alignment(align(s1, s2, compute_backpointers(s1, s2)))
            print('Success! Your results are correct')
        else:
            print('Your results:\n')
            print_alignment(align(s1, s2, compute_backpointers(s1, s2)))
            print("The server's results\n")
            print_alignment(response_data['result'])
            print("Your results differ from the server's results")
    else:
        print_alignment(align(s1, s2, compute_backpointers(s1, s2)))


if __name__ == "__main__":
    main()
