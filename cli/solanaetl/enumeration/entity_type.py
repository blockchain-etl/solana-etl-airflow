class EntityType:
    ACCOUNT = 'account'
    BLOCK = 'block'
    INSTRUCTION = 'instruction'
    TOKEN_TRANSFER = 'token_transfer'
    TOKEN = 'token'
    TRANSACTION = 'transaction'


    ALL_FOR_STREAMING = [ACCOUNT, BLOCK, INSTRUCTION, TOKEN_TRANSFER, TOKEN, TRANSACTION]
