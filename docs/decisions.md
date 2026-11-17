# General decisions file (fully human, fact checked by AI)

## Dataset filter decisions

* I decided to use OWA (open world assumption) in order to avoid negation-as-failure, which means if a fact that relates to the conclusion doesn't exist, the output must be False. In CWA, negation-as-failure exists, so there are no unknowns, only True and False.

* I decided to drop unknowns for the sake of simplicity for now, still using OWA. I don't want to switch to CWA and allow negation-as-failure to keep things simple.

* I decided to use explicitly rules that have the "someone" or "something" word. I realized that in the previous pilot role experiment, I included rules in the format "If Charlie is red, then Charlie is big", which doesn't analyze binding at all. Maybe this is one of the reasons why we had mixed results and wasn't able to conclude much about binding. These rules can be filtered using the representation field, which writes every rule in either someone/something format, or entity name format.

* I decided to use depth-1 (where the conclusion requires one logical step, as it is in modus ponens and modus tollens). Depth-1 theories also contain depth-0, so I will drop depth-0 theories inside depth-1.

* We use the proofs field to determine whether a question uses a proof with a rule that contains directly the entity. E.g., if the rule is "If Charlie is red then Charlie is big.", there is no binding going on. So the proofs that uses that rule are dropped, hence the rules as well.

* There are some questions that doesn't ask about the entity, especially in Relneg and Relnoneg. The fact is "The bear chases the tiger", and the conlusion says "The tiger is rough". I decided to exclude these from the initial bit.

* If a question is left with no proof after these filters, it gets removed.

* If a question has true and false questions (conclusion) that are not negated versions of each other (if they are not different conclusions with only difference one is affirmative and one is negated), that data point is dropped. We must have the same question, just one is negated version of the other. Otherwise we cannot compare them.

* Basically anything that doesn't relate to binding have been filtered out. The goal is to make our jobs easier, while making sure everything stays valid. I think this is the best approach without creating a dataset tailored for this job so that we can analyze real cases, real-life correlated logical problems.

* I consider every data point (every fact,rule,conclusion triple) one document for bag of words.

- In the end:
train: 5532 theories kept
dev: 815 theories kept
test: 1624 theories kept