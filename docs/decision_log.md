# General decisions file (fully human, fact checked by AI)

## Dataset filter decisions

* I decided to use OWA (open world assumption) in order to avoid negation-as-failure, which means if a fact that relates to the conclusion doesn't exist, the output must be False. In CWA, negation-as-failure exists, so there are no unknowns, only True and False.

* I decided to drop unknowns for the sake of simplicity for now, still using OWA. I don't want to switch to CWA and allow negation-as-failure to keep things simple.

* I decided to use explicitly rules that have the "someone" or "something" word. I realized that in the previous pilot role experiment, I included rules in the format "If Charlie is red, then Charlie is big", which doesn't analyze binding at all. Maybe this is one of the reasons why we had mixed results and wasn't able to conclude much about binding. These rules can be filtered using the representation field, which writes every rule in either someone/something format, or entity name format.

* I decided to use depth-1 (where the conclusion requires one logical step, as it is in modus ponens and modus tollens). Depth-1 theories also contain depth-0, so I will drop depth-0 questions inside depth-1. Plus, later (18-10-2026) I discovered that the 1 in depth-1 questions represent the shortest route, not the only route. So a depth-1 question can contain depth-2 or depth-6 routes to reach to the conclusion. I now removed those routes by removing both the rules and the facts connected to those multi-depth proofs. BUT, if a fact or rule is still being used by another proof, they are kept. 

* We use the proofs field to determine whether a question uses a proof with a rule that contains directly the entity. E.g., if the rule is "If Charlie is red then Charlie is big.", there is no binding going on. So those rules are dropped, along with their proofs.

* There are some questions that doesn't ask about the entity, especially in Relneg and Relnoneg. The fact is "The bear chases the tiger", and the conlusion says "The tiger is rough". I decided to exclude these from the initial bit to make the settings simpler to understand and control. Adding them later is just deleting a filter.

* If a question is left with no proof after these filters, it gets removed.

* If a theory has true and false questions (conclusion) that are not negated versions of each other (if they are not different conclusions with only difference one is affirmative and one is negated), that data point is dropped. We must have the same question, just one is negated version of the other. Otherwise we cannot compare them.

* Basically anything that doesn't relate to binding have been filtered out. The goal is to make our jobs easier, while making sure everything stays valid. I think this is the best approach without creating a dataset tailored for this job so that we can analyze real cases, real-life correlated logical problems.

* The sample-train-seed42.json file contains theories with clutter, and among that clutter there are named-entity rules (If Charlie is red, then Charlie is big). This is ok since these rules are not used to answer the question (statement). They are simply clutter. 
**NOTE**: TURNS OUT IT IS A PROBLEM! They could connect with another question silently. Now every named-entity rule is removed.
In the sample-train-seed42-no-clutter-single-proof.json file, theories are cleaned from clutter and only one proof has been kept (so that we don't have to randomly choose a way to answer the same question).

* I consider every data point (every fact,rule,conclusion triple) one document for bag of words.

* (17-10-2026) After completing the BOW, I realized that having multiple facts will create additional intricacy that we are not concerned with right now, so I decided to pick other examples with only one fact. So I added another filter that removes proofs that require more than one fact, which also removes both the facts and the rules connected to that proof. BUT, if a fact or rule is still being used by another proof, they are kept. This means that the previous results of BOW that are deleted are different, but those doesn't really matter since they weren't part of the plan anyways. I did them out of curiosity.

- In the end:
train: 4481 theories kept
dev: 657 theories kept
test: 1306 theories kept