import torch
from transformers import AutoTokenizer, AutoModelWithLMHead


tokenizer = AutoTokenizer.from_pretrained('t5-base')
model = AutoModelWithLMHead.from_pretrained('t5-base', return_dict=True)

sequence = ("In May, Churchill was still generally unpopular with many Conservatives and probably most of the Labour Party. Chamberlain "
            "remained Conservative Party leader until October when ill health forced his resignation. By that time, Churchill had won the "
            "doubters over and his succession as party leader was a formality."
            " "
            "He began his premiership by forming a five-man war cabinet which included Chamberlain as Lord President of the Council, "
            "Labour leader Clement Attlee as Lord Privy Seal (later as Deputy Prime Minister), Halifax as Foreign Secretary and Labour's "
            "Arthur Greenwood as a minister without portfolio. In practice, these five were augmented by the service chiefs and ministers "
            "who attended the majority of meetings. The cabinet changed in size and membership as the war progressed, one of the key "
            "appointments being the leading trades unionist Ernest Bevin as Minister of Labour and National Service. In response to "
            "previous criticisms that there had been no clear single minister in charge of the prosecution of the war, Churchill created "
            "and took the additional position of Minister of Defence, making him the most powerful wartime Prime Minister in British "
            "history. He drafted outside experts into government to fulfil vital functions, especially on the Home Front. These included "
            "personal friends like Lord Beaverbrook and Frederick Lindemann, who became the government's scientific advisor."
            " "
            "At the end of May, with the British Expeditionary Force in retreat to Dunkirk and the Fall of France seemingly imminent, "
            "Halifax proposed that the government should explore the possibility of a negotiated peace settlement using the still-neutral "
            "Mussolini as an intermediary. There were several high-level meetings from 26 to 28 May, including two with the French "
            "premier Paul Reynaud. Churchill's resolve was to fight on, even if France capitulated, but his position remained precarious "
            "until Chamberlain resolved to support him. Churchill had the full support of the two Labour members but knew he could not "
            "survive as Prime Minister if both Chamberlain and Halifax were against him. In the end, by gaining the support of his outer "
            "cabinet, Churchill outmanoeuvred Halifax and won Chamberlain over. Churchill believed that the only option was to fight on "
            "and his use of rhetoric hardened public opinion against a peaceful resolution and prepared the British people for a long war "
            "– Jenkins says Churchill's speeches were 'an inspiration for the nation, and a catharsis for Churchill himself'."
            " "
            "His first speech as Prime Minister, delivered to the Commons on 13 May was the 'blood, toil, tears and sweat' speech. It was "
            "little more than a short statement but, Jenkins says, 'it included phrases which have reverberated down the decades'.")

inputs = tokenizer.encode("summarize: " + sequence,
                          return_tensors='pt',
                          max_length=512,
                          truncation=True)

summary_ids = model.generate(
    inputs, max_length=150, min_length=80, length_penalty=5., num_beams=2)
summary = tokenizer.decode(summary_ids[0])
print(summary)
