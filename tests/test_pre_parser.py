from kaeru_parser import add_numbers


class TestClass:
    def test_E(self):
        text = add_numbers('tests/E.txt')
        assert_text = open('tests/E_correct.txt').read()
        assert text == assert_text

    def test_F(self):
        text = add_numbers('tests/F.txt')
        assert_text = open('tests/F_correct.txt').read()
        print(text)
        assert text == assert_text
