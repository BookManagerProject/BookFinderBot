def is_valid_isbn(isbn):
    """
    Verifica se la stringa di testo in input rappresenta un ISBN valido.
    Restituisce True se l'ISBN è valido, False altrimenti.
    """
    isbn = isbn.replace(' ', '').replace('-', '')

    # Verifica se la lunghezza dell'ISBN è corretta (deve essere di 10 o 13 cifre)
    if len(isbn) != 10 and len(isbn) != 13:
        return False

    # Calcola il valore del controllo di verifica (ultima cifra dell'ISBN)
    check_digit = None
    if len(isbn) == 10:
        # Per gli ISBN a 10 cifre, il controllo di verifica può essere una cifra o la lettera 'X'
        if not isbn[:-1].isdigit():
            return False
        check_digit = int(isbn[-1]) if isbn[-1].isdigit() else 10
        if check_digit == 10 and isbn[-1] != 'X':
            return False
    elif len(isbn) == 13:
        # Per gli ISBN a 13 cifre, il controllo di verifica deve essere una cifra
        if not isbn.isdigit():
            return False
        check_digit = int(isbn[-1])

    # Calcola il valore atteso del controllo di verifica
    expected_check_digit = None
    if len(isbn) == 10:
        expected_check_digit = sum((i + 1) * int(c) for i, c in enumerate(isbn[:-1])) % 11
        expected_check_digit = 11 - expected_check_digit if expected_check_digit != 0 else 0
    elif len(isbn) == 13:
        expected_check_digit = (10 - sum((3 if i % 2 == 0 else 1) * int(c) for i, c in enumerate(isbn[:-1]))) % 10

    # Confronta il valore calcolato del controllo di verifica con quello atteso
    return check_digit == expected_check_digit
