import string
import sys
import Hanzi_Break
from pypinyin import lazy_pinyin


# 检测命令行参数
def parameter():
    if len(sys.argv) != 4:
        print("命令行参数错误!")
        raise Exception("命令行参数错误")


parameter()

# 通过命令行参数读取文件
word_addr = (sys.argv[1])  # 敏感词文件
org_addr = (sys.argv[2])  # 待检测文本
ans_addr = (sys.argv[3])  # 答案输出文件


# 由命令行参数打开文件并对异常进行处理
def open_file(path):
    try:
        file = open(path, 'r+', encoding='utf-8')
    except Exception:
        print("文件打开失败!")
        raise Exception("文件打开失败")
    else:
        return file


class chinese:
    def __init__(self, sensitive_word):
        self.sensitive_word = sensitive_word
        self.length = len(sensitive_word)  # 长度
        self.pinyin = lazy_pinyin(sensitive_word)  # 拼音
        self.pinyinLen = []  # 拼音长度
        self.hanzibreak = []
        for pinyin in self.pinyin:
            self.pinyinLen.append(len(pinyin))
        for w in sensitive_word:
            s = Hanzi_Break.break_hanzi(w)
            if s != "0":
                self.hanzibreak.append(s)
            else:
                self.hanzibreak.append("")

    # 对待检测文本的一行检测汉语敏感词
    def matching(self, wd):
        text = ""
        str = "".join(lazy_pinyin(wd[0]))
        if str[0] == self.pinyin[0][0] or wd[0].lower() == self.pinyin[0][0] or wd[0] == self.hanzibreak[0][0]:
            i = 0
            j = 0
            insert = 0
            while (j < len(wd)):
                if i == self.length or insert > 20:
                    break
                str1 = "".join(lazy_pinyin(wd[j]))
                if j + 2 <= len(wd) and wd[j:j + 2] == self.hanzibreak[i]:
                    text += wd[j:j + 2]
                    j += 1
                    i += 1
                    insert = 0
                elif str1 == self.pinyin[i]:
                    text += wd[j]
                    i += 1
                    insert = 0
                elif j + self.pinyinLen[i] <= len(wd) and (wd[j:j + self.pinyinLen[i]]).lower() == self.pinyin[i]:  # 全拼音
                    text += wd[j:j + self.pinyinLen[i]]
                    j = j + self.pinyinLen[i] - 1
                    i += 1
                    insert = 0
                elif wd[j].lower() == self.pinyin[i][0]:
                    text += wd[j]
                    i += 1
                    insert = 0
                elif wd[j] in string.digits + string.ascii_letters + "[\n`~!@#$%^&*()+-_=|{}':;',\\[\\].<>/?~！\"@#￥%……&*()——+|{}【】‘；：”“’。， 、？]":
                    text += wd[j]
                    insert += 1
                else:
                    break
                j += 1
            if i != self.length:
                text = ""
        return text, len(text)


class english:
    def __init__(self, sensitive_word):
        self.sensitive_word = sensitive_word
        self.length = len(sensitive_word)

    def matching(self, wd):
        text = ""
        i = 0
        if wd[0].lower() == self.sensitive_word[0].lower():
            i = 1
            text += wd[0]
            for j in range(1, len(wd)):
                if i == self.length:
                    break
                if wd[j].lower() == self.sensitive_word[i].lower():
                    text += wd[j]
                    i += 1
                elif wd[j] in string.digits + "[\n`~!@#$%^&*()+=|{}':;',\\[\\].<>/?~！@#￥%……&*()——+|{}【】\"‘；：”“’。， 、？]":
                    text += wd[j]
                else:
                    break
            if i != self.length:
                text = ""
        return text, len(text)


# 读入敏感词文件并根据敏感词类型,中文还是英文,存入list
def read_sensitive_word(path):
    chinese_sensitive_word = []
    english_sensitive_word = []
    file = open_file(path)
    for line in file.readlines():
        line = line.strip()
        if line[0] in string.ascii_letters:  # 根据敏感词首个字符是否为字母判断敏感词是中文还是英文
            english_sensitive_word.append(english(line))
        else:
            chinese_sensitive_word.append(chinese(line))
    file.close()
    return chinese_sensitive_word, english_sensitive_word


def search(lines, chiWords, engWords):
    lineCount = 0
    result = []
    totalCount = 0      # 敏感词个数
    textLen = 0
    for line in lines:  # 读取每行
        lineCount += 1
        line = line.strip()
        i = 0
        while (i < len(line)):
            for wd in engWords:
                text, textLen = wd.matching(line[i:])
                if textLen:
                    totalCount += 1
                    result.append("Line{}: <{}> {}".format(lineCount, wd.sensitive_word, text))
                    i += textLen - 1
                    break
            for wd in chiWords:
                text, textLen = wd.matching(line[i:])
                if textLen:
                    totalCount += 1
                    result.append("Line{}: <{}> {}".format(lineCount, wd.sensitive_word, text))
                    i += textLen - 1
                    break
            i += 1
    return result, totalCount


def main():
    # 敏感词读取
    chiWords, engWords = read_sensitive_word(word_addr)

    # 文本检测
    textFile = open_file(org_addr)
    lines = textFile.readlines()
    result, total = search(lines, chiWords, engWords)
    textFile.close()

    # 写入文件
    answerFile = open_file(ans_addr)
    answerFile.write("Total: {} ".format(total) + '\n')
    answerFile.write('\n'.join(result))
    answerFile.close()


if __name__ == '__main__':
    main()
