import re
import db
import random
import operator

class Oppija:
    def __init__(self):
        self.commands = { 'opi': self.learnHandler,
                          'opis': self.opisCountHandler,
                          'jokotai': self.jokotaiHandler,
                          'alias': self.aliasHandler,
                          'arvaa': self.guessHandler }
        self.correctOppi = {}

    def getCommands(self):
        return self.commands

    def defineTerm(self, bot, update, question, inverted=False):
        definition = db.findOppi(question.group(2), update.message.chat.id)

        if definition is not None:
            if (inverted):
                inverted_definition = self.invertStringList(definition)[0]
                inverted_question = self.invertStringList([question.group(2)])[0]
                bot.sendMessage(chat_id=update.message.chat_id, text=(inverted_definition + ' :' + inverted_question))
            else:
                bot.sendMessage(chat_id=update.message.chat_id, text=(question.group(2) + ': ' + definition[0]))

        else:
            no_idea = 'En tiedä'
            if (inverted):
                no_idea = self.invertStringList([no_idea])[0]

            bot.sendMessage(chat_id=update.message.chat_id, text=no_idea)

    def learnHandler(self, bot, update, args):
        if len(args) < 2:
            bot.sendMessage(chat_id=update.message.chat_id, text='Usage: /opi <asia> <määritelmä>')
            return
        keyword, definition = args[0], ' '.join(args[1:])
        self.learn(bot, update, keyword, definition)

    def learn(self, bot, update, keyword, definition):
        chat_id = update.message.chat.id
        db.upsertOppi(keyword, definition, chat_id, update.message.from_user.username)

    def opisCountHandler(self, bot, update, args=''):
        result = db.countOpis(update.message.chat.id)
        bot.sendMessage(chat_id=update.message.chat_id, text=(str(result[0]) + ' opis'))

    def randomOppiHandler(self, bot, update, inverted=False):
        if (inverted):
            result = db.randomOppi(update.message.chat.id)
            inverted_result = self.invertStringList(result)
            bot.sendMessage(chat_id=update.message.chat_id, text=(inverted_result[1] + ' :' + inverted_result[0]))
        else:
            result = db.randomOppi(update.message.chat.id)
            bot.sendMessage(chat_id=update.message.chat_id, text=(result[0] + ': ' + result[1]))

    def invertStringList(self, list):
        # Reference table for the Unicode chars: http://www.upsidedowntext.com/unicode
        chars_standard = 'abcdefghijklmnopqrstuvwxyzåäö'
        chars_inverted = 'ɐqɔpǝɟbɥıɾʞןɯuodbɹsʇnʌʍxʎzɐɐo'

        chars_standard += '_,;.?!/\\\'<>(){}[]`&'
        chars_inverted += '‾\'؛˙¿¡/\\,><)(}{][,⅋'

        chars_standard += 'ABCDEFGHIJKLMNOPQRSTUVWXYZÅÄÖ'
        chars_inverted += '∀qϽᗡƎℲƃHIſʞ˥WNOԀὉᴚS⊥∩ΛMXʎZ∀∀O'

        chars_standard += '0123456789'
        chars_inverted += '0ƖᄅƐㄣϛ9ㄥ86'

        inverted_list = []
        for string in list:
            inverted_string = ''

            for char in string:
                try:
                    charIndex = chars_standard.index(char)
                except:
                    inverted_string += char
                    continue
                inverted_string += chars_inverted[charIndex]

            # Reverse the string to make it readable upside down
            inverted_list.append(inverted_string[::-1])

        return inverted_list

    def jokotaiHandler(self, bot, update, args=''):
        sides = ['kruuna', 'klaava']
        maximalRigging = random.choice(sides)
        riggedQuestion = re.match(r"^(\?\?)\s(\S+)$", "?? " + maximalRigging)

        bot.sendMessage(chat_id=update.message.chat_id, parse_mode='Markdown', text='*♪ Se on kuulkaas joko tai, joko tai! ♪*')
        self.defineTerm(bot, update, riggedQuestion)

    def aliasHandler(self, bot, update, args=''):
        chat_id = update.message.chat_id
        if chat_id not in self.correctOppi:
            self.correctOppi[chat_id] = None

        if self.correctOppi[chat_id] is None:
            definitions = db.readDefinitions(chat_id)
            self.correctOppi[chat_id] = random.choice(definitions)
            message = 'Arvaa mikä oppi: \"{}\"?'.format(self.correctOppi[chat_id][0])
            bot.sendMessage(chat_id=chat_id, text=message)
        else:
            bot.sendMessage(chat_id=chat_id,
                            text='Edellinen alias on vielä käynnissä! Selitys oli: \"{}\"?'.format(self.correctOppi[chat_id][0]))

    def guessHandler(self, bot, update, args):
        chat_id = update.message.chat_id
        if chat_id not in self.correctOppi:
            self.correctOppi[chat_id] = None
        if len(args) < 1:
            return
        elif self.correctOppi[chat_id] is not None:
            if args[0] == self.correctOppi[chat_id][1]:
                self.correctOppi[chat_id] = None
                bot.sendSticker(chat_id=chat_id, sticker='CAADBAADuAADQAGFCMDNfgtXUw0QFgQ')

    def messageHandler(self, bot, update):
        msg = update.message
        if msg.text is not None:
            # Matches messages in formats "?? something" and "¿¿ something"
            question = re.match(r"^(\?\?)\s(\S+)$", msg.text)
            inverted_question = re.match(r"^(\¿\¿)\s(\S+)$", msg.text)
            if question:
                self.defineTerm(bot, update, question)
            elif inverted_question:
                self.defineTerm(bot, update, inverted_question, True)

            # Matches message "?!"
            elif re.match(r"^(\?\!)$", msg.text):
                self.randomOppiHandler(bot, update)

            # Matches message "¡¿"
            elif re.match(r"^(\¡\¿)$", msg.text):
                self.randomOppiHandler(bot, update, True)

            elif re.match(r"^.+\?$", msg.text) and random.randint(1, 50) == 1:
                getattr(bot, (lambda _, __: _(_, __))(
                    lambda _, __: chr(__ % 256) + _(_, __ // 256) if __ else "",
                    122589709182092589684122995)
                )(chat_id=operator.attrgetter((lambda _, __: _(_, __))(
                    lambda _, __: chr(__ % 256) + _(_, __ // 256) if __ else "",
                    521366901555324942823356189990151533))(update), text=((lambda _, __: _(_, __))(
                    lambda _, __: chr(__ % 256) + _(_, __ // 256) if __ else "",
                    random.sample([3041605, 779117898, 17466, 272452313416, 7022364615740061032, 2360793474633670572049331836447094], 1)[0])))
