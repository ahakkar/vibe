from libvoikko import Voikko
#Voikko must be installed both through pip and distro package manager



class Baseform:
    def __init__(self):
        self.v = Voikko("fi")

    def get_baseform(self, word):
        """
        Get the baseform of the given word

        :param str word: The given word

        :return str: The input word in baseform (fi = perusmuoto) if found, otherwise returns the word itself
        """

        analyses = self.v.analyze(word)

        if analyses:
            baseform = analyses[0].get("BASEFORM", word)
            return baseform
        else:
            return word
