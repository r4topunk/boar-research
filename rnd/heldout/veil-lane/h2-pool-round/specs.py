# H2 pool round 2: candidate specs (template, lang, question, pages, answer, verify=[(page, [tokens])], shape)
S = [
 # T1 EN: What is the population/area/height/length of X?
 ("T1","en","What is the area of Madagascar?",["Madagascar"],"About 587,041 km².",[("Madagascar",["587,041","587,295","592,800"])],"numeric"),
 ("T1","en","What is the height of the Matterhorn?",["Matterhorn"],"About 4,478 m (14,692 ft).",[("Matterhorn",["4,478"])],"numeric"),
 ("T1","en","What is the length of the Nile?",["Nile"],"About 6,650 km by the traditional figure; the article now gives 7,088 km (4,404 mi) from a newer source measurement.",[("Nile",["7,088","6,650"])],"numeric"),
 ("T1","en","What is the area of Greenland?",["Greenland"],"About 2,166,086 km².",[("Greenland",["2,166,086"])],"numeric"),
 ("T1","en","What is the height of Angel Falls?",["Angel Falls"],"About 979 m (3,212 ft), the world's tallest uninterrupted waterfall.",[("Angel Falls",["979"])],"numeric"),
 ("T1","en","What is the length of the Yangtze?",["Yangtze"],"About 6,300 km (the article gives 6,236 km, 3,875 mi).",[("Yangtze",["6,236","6,300"])],"numeric"),
 ("T1","en","What is the area of Lake Superior?",["Lake Superior"],"About 82,100 km² (31,700 sq mi).",[("Lake Superior",["82,100","82,000","31,700"])],"numeric"),
 ("T1","en","What is the population of Norway?",["Norway"],"About 5.6 million.",[("Norway",["5.5 million","5.6 million","5.5 million","5,5"])],"numeric"),
 # T2 PT: Qual é a altura/área/população/capital/frequência de X?
 ("T2","pt","Qual é a capital da Mongólia?",["Mongolia"],"Ulaanbaatar (Ulan Bator).",[("Mongolia",["Ulaanbaatar"])],"lookup"),
 ("T2","pt","Qual é a altura do K2?",["K2"],"Cerca de 8.611 m, a segunda montanha mais alta do mundo.",[("K2",["8,611"])],"numeric"),
 ("T2","pt","Qual é a capital do Marrocos?",["Morocco"],"Rabat (Casablanca é a maior cidade).",[("Morocco",["Rabat"])],"lookup"),
 ("T2","pt","Qual é a capital do Cazaquistão?",["Kazakhstan"],"Astana.",[("Kazakhstan",["Astana"])],"lookup"),
 ("T2","pt","Qual é a capital da Bolívia?",["Bolivia"],"Sucre é a capital constitucional; La Paz é a sede do governo.",[("Bolivia",["Sucre"]),("Bolivia",["La Paz"])],"lookup"),
 ("T2","pt","Qual é a área do Mar Cáspio?",["Caspian Sea"],"Cerca de 371.000 km², o maior corpo de água interior do mundo.",[("Caspian Sea",["371,000"])],"numeric"),
 ("T2","pt","Qual é a capital da Nigéria?",["Nigeria"],"Abuja.",[("Nigeria",["Abuja"])],"lookup"),
 ("T2","pt","Qual é a capital do Vietnã?",["Vietnam"],"Hanói (Hanoi).",[("Vietnam",["Hanoi"])],"lookup"),
 # T3 PT: Quantos/Quantas N tem X? / Quanto tempo ...?
 ("T3","pt","Quantos estados tem os Estados Unidos?",["United States"],"50 estados (mais o Distrito de Colúmbia).",[("United States",["50 states"])],"numeric"),
 ("T3","pt","Quantas províncias tem o Canadá?",["Canada"],"10 províncias (e 3 territórios).",[("Canada",["ten provinces","10 provinces"])],"numeric"),
 ("T3","pt","Quantos estados tem a Austrália?",["Australia"],"6 estados (e territórios continentais).",[("Australia",["six states","6 states"])],"numeric"),
 ("T3","pt","Quantos cantões tem a Suíça?",["Switzerland"],"26 cantões.",[("Switzerland",["26 cantons"])],"numeric"),
 ("T3","pt","Quantos andares tem o Burj Khalifa?",["Burj Khalifa"],"163 andares (acima do solo).",[("Burj Khalifa",["163"])],"numeric"),
 ("T3","pt","Quantos anos durou a Guerra dos Cem Anos?",["Hundred Years' War"],"116 anos (1337–1453).",[("Hundred Years' War",["1337","1453"])],"numeric"),
 ("T3","pt","Quanto tempo dura um dia em Marte?",["Mars"],"Cerca de 24 horas e 39 minutos (um sol marciano: 24 h 39 min 35 s).",[("Mars",["24 hours, 39 minutes"])],"numeric"),
 ("T3","pt","Quantas pessoas morreram no naufrágio do Titanic?",["Titanic"],"Mais de 1.500 pessoas.",[("Titanic",["1,500"])],"numeric"),
 # T4 EN: When was/did X?
 ("T4","en","When was the Magna Carta sealed by King John?",["Magna Carta"],"In 1215 (15 June).",[("Magna Carta",["1215"])],"year"),
 ("T4","en","When was the Eiffel Tower completed?",["Eiffel Tower"],"In 1889.",[("Eiffel Tower",["1889"])],"year"),
 ("T4","en","When did the Hindenburg disaster happen?",["Hindenburg disaster"],"On 6 May 1937.",[("Hindenburg disaster",["1937"])],"year"),
 ("T4","en","When was the Panama Canal opened?",["Panama Canal"],"In 1914 (15 August).",[("Panama Canal",["1914"])],"year"),
 # T4 PT: Em que ano ...?
 ("T4","pt","Em que ano foi fundada a ONU?",["United Nations"],"Em 1945.",[("United Nations",["1945"])],"year"),
 ("T4","pt","Em que ano terminou a Guerra Fria?",["Cold War"],"Em 1991, com a dissolução da União Soviética.",[("Cold War",["1991"])],"year"),
 ("T4","pt","Em que ano o Brasil se tornou independente?",["Brazil"],"Em 1822.",[("Brazil",["1822"])],"year"),
 ("T4","pt","Em que ano Cristóvão Colombo chegou à América?",["Christopher Columbus"],"Em 1492.",[("Christopher Columbus",["1492"])],"year"),
 # T5 EN: Which N is more X, A or B?
 ("T5","en","Which river is longer, the Volga or the Danube?",["Volga","Danube"],"The Volga, about 3,531 km vs about 2,850 km for the Danube.",[("Volga",["3,531","3,530"]),("Danube",["2,850"])],"comparative"),
 ("T5","en","Which mountain is higher, K2 or Kangchenjunga?",["K2","Kangchenjunga"],"K2, about 8,611 m vs about 8,586 m for Kangchenjunga.",[("K2",["8,611"]),("Kangchenjunga",["8,586"])],"comparative"),
 ("T5","en","Which ocean is larger, the Atlantic or the Indian Ocean?",["Atlantic Ocean","Indian Ocean"],"The Atlantic: about 85-106 million km² (with or without marginal seas) vs about 70.6 million km² for the Indian Ocean.",[("Atlantic Ocean",["106,460,000","85,133,000"]),("Indian Ocean",["70,560,000"])],"comparative"),
 ("T5","en","Which planet is larger, Uranus or Neptune?",["Uranus","Neptune"],"Uranus (slightly larger in diameter; Neptune is more massive).",[("Uranus",["third-largest","third largest"]),("Neptune",["fourth-largest","fourth largest"])],"comparative"),
 # T5 PT: Qual N é mais X, A ou B?
 ("T5","pt","Qual lago é maior, o Superior ou o Vitória?",["Lake Superior","Lake Victoria"],"O Lago Superior (cerca de 82.100 km², contra cerca de 59.900–68.800 km² do Vitória).",[("Lake Superior",["82,100","82,000"]),("Lake Victoria",["59,947","68,800","59,947"])],"comparative"),
 ("T5","pt","Qual deserto é maior, o Saara ou o Gobi?",["Sahara","Gobi Desert"],"O Saara (cerca de 9,2 milhões de km², contra cerca de 1,3 milhão do Gobi).",[("Sahara",["9,200,000","9.2 million"]),("Gobi Desert",["1,295,000","1.3 million","500,000"])],"comparative"),
 ("T5","pt","Qual montanha é mais alta, o Kilimanjaro ou o Monte Quênia?",["Mount Kilimanjaro","Mount Kenya"],"O Kilimanjaro (cerca de 5.895 m, contra cerca de 5.199 m do Monte Quênia).",[("Mount Kilimanjaro",["5,895"]),("Mount Kenya",["5,199"])],"comparative"),
 ("T5","pt","Qual cidade é mais populosa, São Paulo ou Rio de Janeiro?",["São Paulo","Rio de Janeiro"],"São Paulo: cerca de 11,4 milhões na cidade e mais de 20 milhões na região metropolitana, contra cerca de 6 milhões na cidade do Rio (13 milhões na metrópole).",[("São Paulo",["20 million"]),("Rio de Janeiro",["6 million"])],"comparative"),
 # T6 EN: Is A higher/larger/older than B?
 ("T6","en","Is Mount Rainier higher than Mount Fuji?",["Mount Rainier","Mount Fuji"],"Yes: about 4,392 m vs about 3,776 m.",[("Mount Rainier",["4,392"]),("Mount Fuji",["3,776"])],"yes/no"),
 ("T6","en","Is Lake Michigan larger than Lake Huron?",["Lake Michigan","Lake Huron"],"No: Lake Huron is slightly larger (about 59,570 km² vs about 58,030 km² for Lake Michigan).",[("Lake Michigan",["58,030","57,757"]),("Lake Huron",["59,570"])],"yes/no"),
 ("T6","en","Is the University of Oxford older than the University of Cambridge?",["University of Oxford","University of Cambridge"],"Yes: teaching at Oxford existed by 1096; Cambridge was founded in 1209.",[("University of Oxford",["1096"]),("University of Cambridge",["1209"])],"yes/no"),
 ("T6","en","Is the Mekong longer than the Yellow River?",["Mekong","Yellow River"],"No: the Yellow River is about 5,464 km and the Mekong about 4,909 km.",[("Mekong",["4,909","4,900"]),("Yellow River",["5,464"])],"yes/no"),
 ("T6","en","Is Jupiter larger than Saturn?",["Jupiter","Saturn"],"Yes: Jupiter is the largest planet in the Solar System; Saturn is second.",[("Jupiter",["largest planet"]),("Saturn",["second-largest","second largest"])],"yes/no"),
 # T6 PT: É A maior que B?
 ("T6","pt","É o Canadá maior que os Estados Unidos em área?",["Canada","United States"],"Sim: o Canadá tem cerca de 9,98 milhões de km², os EUA cerca de 9,5-9,8 milhões.",[("Canada",["9.98 million","9,984,670","second-largest"]),("United States",["9.8 million","3.8 million","third-largest","fourth-largest"])],"yes/no"),
 ("T6","pt","É a Rússia maior que a Antártida?",["Russia","Antarctica"],"Sim: a Rússia tem cerca de 17,1 milhões de km², a Antártida cerca de 14,2 milhões.",[("Russia",["17,098,246","17.1 million","largest country"]),("Antarctica",["14,200,000","14.2 million"])],"yes/no"),
 ("T6","pt","É o rio Amazonas mais longo que o Mississippi?",["Amazon River","Mississippi River"],"Sim: o Amazonas tem cerca de 6.400 km, o Mississippi cerca de 3.766 km.",[("Amazon River",["6,400"]),("Mississippi River",["3,766","2,340"])],"yes/no"),
 # T7 EN: Which country has the most / is the largest ...?
 ("T7","en","Which country is the largest by area?",["Russia"],"Russia.",[("Russia",["largest country"])],"superlative"),
 ("T7","en","Which country has the largest population?",["India"],"India (since 2023, ahead of China).",[("India",["most populous"])],"superlative"),
 ("T7","en","Which is the largest ocean on Earth?",["Pacific Ocean"],"The Pacific Ocean.",[("Pacific Ocean",["largest"])],"superlative"),
 ("T7","en","Which is the smallest country in the world?",["Vatican City"],"Vatican City.",[("Vatican City",["smallest"])],"superlative"),
 ("T7","en","Which is the hottest planet in the Solar System?",["Venus"],"Venus.",[("Venus",["hottest"])],"superlative"),
 # T7 PT: Qual país/estado/cidade tem mais/é o maior ...?
 ("T7","pt","Qual é o maior país da América do Sul?",["Brazil"],"O Brasil.",[("Brazil",["largest country in South America","largest country in both South America"])],"superlative"),
 ("T7","pt","Qual país tem a maior população da África?",["Nigeria"],"A Nigéria.",[("Nigeria",["most populous country in Africa"])],"superlative"),
 ("T7","pt","Qual é o maior país da África?",["Algeria"],"A Argélia.",[("Algeria",["largest country in Africa"])],"superlative"),
 # T8 EN: Which countries border X? / Who was ...?
 ("T8","en","Which countries border Portugal?",["Portugal"],"Only Spain.",[("Portugal",["Spain"])],"lookup"),
 ("T8","en","Which countries border Bolivia?",["Bolivia"],"Brazil, Paraguay, Argentina, Chile and Peru.",[("Bolivia",["Paraguay"]),("Bolivia",["Peru"])],"list"),
 ("T8","en","Who was the first president of the United States?",["George Washington"],"George Washington.",[("George Washington",["first president"])],"lookup"),
 ("T8","en","Who was the first emperor of Rome?",["Augustus"],"Augustus.",[("Augustus",["first Roman emperor","first emperor"])],"lookup"),
 ("T8","en","Who painted the Mona Lisa?",["Mona Lisa"],"Leonardo da Vinci.",[("Mona Lisa",["Leonardo da Vinci"])],"lookup"),
 # T8 PT: Quem foi ... / Quais países fazem fronteira com X?
 ("T8","pt","Quem foi o primeiro imperador do Brasil?",["Pedro I of Brazil"],"Dom Pedro I.",[("Pedro I of Brazil",["first monarch","Emperor of Brazil","first emperor"])],"lookup"),
 ("T8","pt","Quem descobriu a penicilina?",["Penicillin"],"Alexander Fleming, em 1928.",[("Penicillin",["Fleming"])],"lookup"),
 ("T8","pt","Quais países fazem fronteira com o Uruguai?",["Uruguay"],"Brasil e Argentina.",[("Uruguay",["Brazil"]),("Uruguay",["Argentina"])],"list"),
]
