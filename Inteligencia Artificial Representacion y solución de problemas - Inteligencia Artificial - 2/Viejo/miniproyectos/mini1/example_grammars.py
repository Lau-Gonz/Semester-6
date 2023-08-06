from random import randint, choice, uniform

class ExampleGrammars():


    def __init__(self):

        self.grammars = {

            # grammar of the form:
            # a^{i} b^{i}, that is, same number of a's and b's.
            # where i is an integer.
            1:    [('S', 'aSb'), ('S', 'AB'),
                   ('A', 'a'), ('B', 'b')], 

            # grammar of the form:
            # a^{j} b^{i} c^{i} d^{j}, i, j >= 0, same number of a's and c's, 
            # and same number of b's and d's, where i and j are integers.

            2:    [('S', 'aWd'), ('W', 'aWd'), ('W', 'V'),
                   ('V', 'bVc'), ('V', 'X'), ('X', 'bc')],


            # grammar of the form:
            # a^{i} b^{j}, i>j>0, that means a's are more than b's.
            3:    [('S', 'aR'), ('R', 'aRb'), 
                   ('R', 'aR'), ('R', 'aW'), ('W', 'b')],

            # grammar of the form:
            # the alphabet is {0, 1}, and the grammar is:
            # where the words are palindromes. ex: 10101, 01010, 1001, 1111, 0000 etc.
            4:    [('S', 'CA'), ('S', 'DB'), ('S', '1'), 
                   ('S', '0'), ('S', 'CC'), ('S', 'DD'),
                   ('A', 'SC'), ('B', 'SD'), ('C', '1'),
                   ('D', '0')]


        }

    def get_grammar(self, grammar_num: int):

        return self.grammars[grammar_num]


    def generate_word(self, grammar_num: int, word_interval_len: tuple):

        """
            Generates a word from a grammar. This could be done by a recursive function,
            or going through the grammar and generating a word from each rule. but
            I felt lazy enough to do it this way.
        """

        if grammar_num not in self.grammars.keys():

            print("Please select a valid grammar number")
            print("available grammars: {}".format(self.grammars.keys()))
            return None 

        ans = ""
    
        if grammar_num == 1:
            ans = self.generate_word_grammar1(word_interval_len)
        
        elif grammar_num == 2:
            ans = self.generate_word_grammar2(word_interval_len)

        elif grammar_num == 3:
            ans = self.generate_word_grammar3(word_interval_len)

        elif grammar_num == 4:
            ans = self.generate_word_grammar4(word_interval_len)

        return ans

    def generate_word_grammar1(self, word_interval_len: tuple) -> str:

        """
            Generates a word from the grammar 1.
            Input: word_interval_len -> tuple, is the interval of the word length.
                   meaning the word length will be between the values of the tuple.
        """

        i = randint(word_interval_len[0]//2 , word_interval_len[1]//2)

        return ("a"*i) + ("b"*i)

    def generate_word_grammar2(self, word_interval_len: tuple) -> str:


        """
            Generates a word from the grammar 2.
            Input: word_interval_len -> tuple, is the interval of the word length.
                   meaning the word length will be between the values of the tuple.
        """

        i = randint((word_interval_len[0])//4 , ((word_interval_len[1])//4))
        j = randint((word_interval_len[0] + 1)//4 , ((word_interval_len[1] - i)//4))

        n = choice((i, j)) 
        m = j if n == i else i

        return ("a"*n) + ("b"*m) + ("c"*m) + ("d"*n)


    def generate_word_grammar3(self, word_interval_len: tuple) -> str:


        """
            Generates a word from the grammar 2.
            Input: word_interval_len -> tuple, is the interval of the word length.
                   meaning the word length will be between the values of the tuple.
        """

        i = randint(word_interval_len[0], word_interval_len[1] - 1)
        remaining_minumum_letters = 1 if (word_interval_len[0] - i) < 0 else word_interval_len[0] - i
        remaining_maximum_letters = 1 if (word_interval_len[1] - i) < 0 else word_interval_len[1] - i

        j = randint(remaining_minumum_letters, remaining_maximum_letters)

        m = i if i > j  else j
        n = i if m ==j else j
        
        return ("a"*m) + ("b"*n)  

    def generate_word_grammar4(self, word_interval_len: tuple) -> str:

        """
            Generates a word from the grammar 4.
            Input: word_interval_len -> tuple, is the interval of the word length.
                   meaning the word length will be between the values of the tuple.
        """

        i = randint((word_interval_len[0])//2 , ((word_interval_len[1])//2))
        j = randint((word_interval_len[0])//2 , ((word_interval_len[1] - i)//2))

        n = choice((i, j)) 
        m = j if n == i else i

        opt = choice((1, 2, 3, 4))

        if opt == 1:
            return ("1"*n) + ("0"*m) + ("1"*n)

        elif opt == 2:
            return ("0"*n) + ("1"*m) + ("0"*n)
        
        elif opt == 3:
            return ("1") + ("01"*m) + ("01")
        
        elif opt == 4:
            return ("0") + ("10"*m) + ("10")



    def generate_exact_word(self, grammar_num: int, wlen: int) -> str:

        """
            Generates a word from a grammar. This could be done by a recursive function,
            or going through the grammar and generating a word from each rule. but
            I felt lazy enough to do it this way.
        """

        if grammar_num not in self.grammars.keys():
                
                print("Please select a valid grammar number")
                print("available grammars: {}".format(self.grammars.keys()))
                return None

        ans = ""

        if grammar_num == 1:
            ans = self.generate_exact_word_grammar1(wlen)

        elif grammar_num == 2:
            ans = self.generate_exact_word_grammar2(wlen)

        elif grammar_num == 3:
            ans = self.generate_exact_word_grammar3(wlen)

        return ans


    def generate_exact_word_grammar1(self, wlen: int) -> str:

        """
            Generates a word from the grammar 1.
            wlen: the length of the word. should be an even number.
        """
        return "a"*(wlen//2) + "b"*(wlen//2)


    def generate_exact_word_grammar2(self, wlen: int) -> str:

        """
            Generates a word from the grammar 2.
            wlen: the length of the word. should be an even number.
        """

        # gets a number between 0 and 1
        r = uniform(0, 1)

        i = int( (r*wlen)//2 )
        j = int( ((1 -r)*wlen)//2 )

        if (i+j) < wlen:
            which = choice((0, 1))

            if which == 0:
                j += 1
            else:
                i += 1


        return ("a"*i) + ("b"*j) + ("c"*j) + ("d"*i)

    def generate_exact_word_grammar3(self, wlen: int) -> str:
            
            """
                Generates a word from the grammar 3.
                wlen: the length of the word. should be an even number.
            """
    
            # gets a number between 0 and 1
            r = uniform(0, 1)
    
            i = int( (r*wlen) )
            j = int( ((1 -r)*wlen) )

            placeholders = i 

            if j >= placeholders:
                i = j
                j = placeholders
            

            if (i+j) < wlen:

                if i > j:
                    i += 1
    
            return ("a"*i) + ("b"*j) 






        
        



