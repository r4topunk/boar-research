import { detectGeoIntent } from "<scratch>";
import { isHealthQuestion } from "<scratch>";
const qs = [
 "vegan restaurants near me","vegan restaurants near Alexanderplatz","Where is the best vegan food in Berlin?","What's good to eat in Berlin for vegans?",
 "vegan restaurants in NYC","best vegan restaurants in New York","vegan restaurants in Berlin, Germany","Why are there so many vegan restaurants in Berlin?",
 "Is there a vegan place nearby?","vegan options nearby","any vegan spots around?","vegan bakery near me","vegan restaurants in são paulo",
 "best vegan restaurant in Mexico City","Where can I eat vegan in Bangkok?","plant-based restaurants near me","veggie food near me",
 "Recommend a vegan restaurant for a date tonight","vegan restaurants in the old town","vegan restaurants in Shibuya","onde comer vegano em Lisboa",
 "I have a peanut allergy, which restaurants near me are safe?","vegan restaurants within walking distance","vegan restaurants close to the Colosseum",
];
for (const q of qs) { const i = detectGeoIntent(q); let h: any = "?"; try { h = isHealthQuestion(q); } catch {} console.log(JSON.stringify(q), "=>", i ? `${i.near.kind}${i.near.kind==="place"?":"+(i.near as any).name:""} diet=${i.diet.join("/")||"-"} text=${i.text??"-"} cand=${(i.placeCandidates??[]).join("|")||"-"}` : "NOT PLACES", "| health=", h); }
