class Word:
    inf = ''
    definition = ''
    fp = ''
    sp = ''
    tp = ''
    fsp = ''
    pl = ''
    spp = ''

    def __init__(inf, definition, fp, sp, tp, fsp, pl, spp):
        self.inf = inf
        self.definition = definition
        self.fp = fp
        self.sp = sp
        self.tp = tp
        self.fsp = fsp
        self.pl = pl
        self. spp = spp


    def soup(words):
        from bs4 import BeautifulSoup
        import requests
        import urllib
        for i in words:
            print(i)
            website = "http://www.conjugation-fr.com/conjugate.php?verb=" + i + "&x=0&y=0"
            r = requests.get(website)
            soup = BeautifulSoup(r.content, 'html5lib')
            soup = str(soup)
            print(soup)
            break
        print(je)

        return je

    def french():
        words = """accepter – to accept
                    adorer – to adore
                    aimer – to like
                    annuler – to cancel
                    apporter – to bring
                    attraper – to catch
                    bavarder – to chat
                    casser – to break
                    chanter – to sing
                    chercher – to look for
                    commander – to order
                    commencer – to begin
                    couper – to cut
                    danser – to dance
                    demander – to ask
                    dessiner – to draw
                    détester – to hate, to detest
                    donner – to give
                    écouter – to listen to
                    emprunter – to borrow
                    enlever – to remove
                    étudier – to study
                    exprimer – to express
                    fermer – to close
                    gagner – to win, to earn
                    garder – to keep
                    goûter – to taste
                    habiter – to live
                    jouer – to play
                    laver – to wash
                    montrer – to show
                    oublier – to forget
                    parler – to speak, to talk
                    penser – to think
                    porter – to wear, to carry
                    présenter – to introduce
                    prêter – to lend
                    refuser – to refuse
                    regarder – to watch
                    rencontrer – to meet by chance
                    rester – to stay, to remain
                    rêver – to dream
                    saluer – to greet
                    sauter – to jump
                    sembler – to seem
                    skier – to ski
                    téléphoner – to telephone
                    tomber – to fall
                    travailler – to work
                    trouver – to find
                    utiliser – to use
                    visiter - to visit
                    voler – to fly
                    abolir – to abolish
                    acceuillir – to welcome
                    accomplir – to accomplish
                    affaiblir – to weaken
                    agir – to act
                    avertir – to warn
                    bâtir – to build
                    bénir – to bless
                    choisir – to choose
                    embellir – to make beautiful
                    envahir – to invade
                    établir – to establish
                    étourdir – to stun
                    finir – to finish
                    franchir – to clear an obstacle
                    grandir – to grow up
                    grossir – to gain weight
                    guérir – to cure
                    investir – to invest
                    maigrir – to lose weight
                    nourrir – to feed
                    obéir – to obey
                    punir – to punish
                    ralentir – to slow down
                    réfléchir – to reflect
                    remplir – to fill
                    réunir – to reunite
                    réussir – to succeed
                    rougir – to blush
                    saisir – to seize
                    vieillir – to grow old
                    attendre – to wait for
                    défendre – to defend
                    dépendre – to depend on
                    descendre – to descend
                    détendre – to relax
                    entendre – to hear
                    étendre – to stretch
                    fendre – to split
                    fondre – to melt
                    mordre – to bite
                    pendre – to hang, to suspend
                    perdre – to lose
                    prétendre – to claim
                    rendre – to give back
                    répandre – to spread, to scatter
                    répondre – to answer
                    tendre – to tighten
                    vendre – to sell"""
        k = 0
        wordArr = {}
        j = 0
        word = ''
        definition = ''
        for i in range(len(words)):
            if (words[i] == ' ' and words[i+2] == ' ' and k < i):
                j = i + 3
                word = words[k:i]
            if (words[i] == '\n'):
                wordArr[word] = words[j:i]
                k = i + 21
        return wordArr


    if __name__ == "__main__":
        arr = french()
        soup(arr)
