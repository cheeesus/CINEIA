def test_password_hashing():
    from app.utils.helpers import hash_password, verify_password
    password = "mysecretpassword"
    hashed = hash_password(password)
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)

def test_check_password_different_hash_same_password():
    from app.utils.helpers import hash_password, verify_password
    password = "anothersecurepassword"
    hashed_pwd1 = hash_password(password)
    hashed_pwd2 = hash_password(password) # bcrypt génère des hachages différents à chaque fois
    assert verify_password(password, hashed_pwd1)
    assert verify_password(password, hashed_pwd2)
    assert hashed_pwd1 != hashed_pwd2