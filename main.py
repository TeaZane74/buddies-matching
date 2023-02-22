
import pandas as pd
import random
from statistics import median, mean


coordonnée_lieu = {'1er':(48.86301,2.33548),
'2ème':(48.8682,2.33548),
'3ème':(48.86256,2.3602),
'4ème':(48.8542,2.35711),
'5ème':(48.84426,2.35025),
'6ème':(48.84946,2.33342),
'7ème':(48.85917,2.27506),
'8ème':(48.87159,2.31111),
'9ème':(48.87769,2.33754),
'10ème':(48.87543,2.3602),
'11ème':(48.8594,2.37737),
'12ème':(48.83929,2.39145),
'13ème':(48.82867,2.35952),
'14ème':(48.83025,2.32519),
'15ème':(48.84064,2.29497),
'16ème':(48.85917,2.27506),
'17ème':(48.88694,2.30459),
'18ème':(48.89214,2.34681),
'19ème':(48.88582,2.38149),
'20ème':(48.86233,2.39969),
'Banlieue nord':(48.9345,2.35688),
'Banlieue nord-est':(48.91016,2.43904),
'Banlieue est':(48.8651,2.44659),
'Banlieue sud-est':(48.808,2.43375),
'Banlieue sud':(48.79601,2.34449),
'Banlieue sud-ouest':(48.81779,2.24948),
'Banlieue ouest':(48.87111,2.20073),
'Banlieue nord-ouest':(48.91329,2.26315)}


def preprocessing(filleul:str,parrain:str):
    filleul = pd.read_csv(filleul, sep=',',quotechar='"')
    parrain = pd.read_csv(parrain, sep=',',quotechar='"')


    rename_col = {'Quel adjectif te qualifierait le mieux ?': 'adjectif', 'Ton pôle principal':'pole', 'Quelle mission te plaît le plus à ESN?':'mission','Avec tes potes, tu préfères?':'activite', 'Combien de filleuls tu veux':'nb_filleuls',"Ton lieu d'habitation pour favoriser la proximité":'lieu'}
    activity = {'Faire une visite culturelle':1, 'Chill dans un parc':2, 'Prendre un verre':3, "Faire la fête jusqu'au bout de la nuit":4}
    adjective = {'Timide':1, 'Calme':2, 'Sociable':3, 'Fêtard':4}
    mission = {'Accueillir et intégrer les étudiants internationaux':1,'Sensibiliser à la mobilité internationale':2, 'Sensibiliser à la mobilité interbationale':2}
    pole = {'Com : communication':'COM','CV : culture et voyage':'CV', 'FS : festif et sportif':'FS','Part : partenariat':'PART', "SBE : Santé et bien être":"SBE","BS : bureau statutaire" : "BS"}

    filleul.rename(columns=rename_col,inplace=True)
    parrain.rename(columns=rename_col,inplace=True)

    
    

    parrain['Nom'] = parrain['Nom'] + " " + parrain['Prénom']
    filleul['Nom'] = filleul['Nom'] + " " + filleul['Prénom']

    filleul.set_index(filleul['Nom'], inplace =True)
    parrain.set_index(parrain['Nom'], inplace =True)

    filleul.drop_duplicates(keep='last', inplace=True)
    parrain.drop_duplicates(keep='last', inplace=True)
    


    filleul['activite'] = filleul['activite'].replace(activity)
    parrain['activite'] = parrain['activite'].replace(activity)

    filleul['adjectif'] = filleul['adjectif'].replace(adjective)
    parrain['adjectif'] = parrain['adjectif'].replace(adjective)

    filleul['mission'] = filleul['mission'].replace(mission)
    parrain['mission'] = parrain['mission'].replace(mission)

    parrain['nb_filleuls_init'] = parrain['nb_filleuls']

    for i in pole : 
        filleul['pole'] = filleul['pole'].str.replace(i,str(pole[i]))
        parrain['pole'] = parrain['pole'].str.replace(i,str(pole[i])) 

    return filleul,parrain





def distance(x: list[int], y: list[int]) -> float:
    """ norme euclidienne """
    assert len(x) == len(y)
    return sum([(i - j) ** 2 for i, j in zip(x, y)]) ** (1/2)

def distance_lieu(filleul: dict, parrain: dict) -> float:
    """ distance physique filleul/parrain """
    d_filleul = coordonnée_lieu[filleul['lieu']]
    d_parrain = coordonnée_lieu[parrain['lieu']]
    return distance(d_filleul, d_parrain)

def distance_caractere(filleul: dict, parrain: dict) -> float:
    """ distance caractère filleul/parrain """
    c_filleul = (filleul['adjectif'], filleul['activite'], filleul['mission'])
    c_parrain = (parrain['adjectif'], parrain['activite'], parrain['mission'])
    return distance(c_filleul, c_parrain)

def mul_pole(filleul: dict, parrain: dict) -> float:
    """ multiplicateur d'utilité par pôle (on souhaite avoir des matchs de pôles différents) """
    if filleul['pole'] == parrain['pole']:
        pole = 0.1
    else:
        pole = 1.0
    return pole

def utilite(filleul: dict, parrain: dict) -> float:
    """ utilité du match ... """
    return mul_pole(filleul, parrain) * (10 - 2.5 * distance_caractere(filleul, parrain) - 5 * distance_lieu(filleul, parrain))

def filter_max(D, parrain, rep_pole):
    """ récupération de l'utilité max, de plus, nous essayons de placer en priorité les parrains du même pôle que le pôle le plus représenté (afin de minimiser le nombre de match du même pôle"""
    
    maxu = [x for x in D if D[x] == D[max(D, key = D.get)]]
    maxu_pole = [x for x in maxu if parrain[x]['pole'] == max(rep_pole, key = rep_pole.get)]
    
    if maxu_pole:
        maxu = maxu_pole 
    return maxu

def update_dict(filleul: dict, parrain: dict):
    """ un match a été fait, on marque le filleul et on
        décrémente les matchs souhaités du parrain
    """
    print(parrain)
    parrain['nb_filleuls'] -= 1
    filleul['parrain'] = True

def condition(filleul: dict) -> bool:
    """ le filleul a-t-il un parrain ? """
    return 'parrain' in filleul

def main():

    filleul, parrain = preprocessing('filleul.csv','parrain.csv')
    rep_pole = filleul['pole'].value_counts().to_dict()

    filleul = filleul.to_dict('index')
    parrain = parrain.to_dict('index')
    
    
    

    tableau_match = {}

    while len([1 for filleul in filleul.values() if filleul.get("parrain", False)]) != len(filleul):

        
        i = random.choice([index for index, filleul in filleul.items() if not condition(filleul)])
        
        if sum([parrain[x]['nb_filleuls'] for x in parrain]) <= 0 :
            filleuls_condition = -1
        else:
            filleuls_condition = 0

        tableau_utilite = {
            index: utilite(filleul[i], parrain)
            for index, parrain in parrain.items()
            if parrain['nb_filleuls'] > filleuls_condition
        }

        


        
        match_i = random.choice(filter_max(tableau_utilite, parrain, rep_pole))
        
       
        tableau_match[i] = {
            'filleul':i,
            'parrain': parrain[match_i]['Nom'],
            'Match Ratio': round(tableau_utilite[match_i]/10, 2)
        }
        update_dict(filleul[i], parrain[match_i])


    return tableau_match, parrain


if __name__ == "__main__":
    
    max_avg = 0
    min_med = 1

    for i in range (0,10000):
        res, parrain = main()

        print(parrain)
        avg = mean([res[x]['Match Ratio'] for x in res])
        med  = median([res[x]['Match Ratio'] for x in res])
        

        if avg > max_avg :
            max_avg = avg
            max_avg_med = med
            res_avg_max = res
            parrain_avg = parrain

        if med < min_med :
            min_med = med
            min_med_avg = avg
            res_med_min = res
            parrain_med = parrain

    
    print(f'Best Mean Option - Mean : {max_avg} - Median : {max_avg_med}\n')
    for match in res_avg_max.values():
        print(f"{match['filleul']} -- {match['parrain']}, Taux de match : {match['Match Ratio']}")
    print(f"Nombre de matchs : {len(res)}")
    print(f"Personne ayant plus de filleuls que demandé : {[x for x in parrain_avg if parrain[x]['nb_filleuls'] < 0]}")


    print('--------------------------------\n\n')

    print(f'Best Median Option - Mean : {min_med} - Median : {min_med_avg}\n')
    for match in res_med_min.values():
        print(f"{match['filleul']} -- {match['parrain']}, Taux de match : {match['Match Ratio']}")
    print(f"Nombre de matchs : {len(res)}")
    print(f"Personne ayant plus de filleuls que demandé : {[x for x in parrain_med if parrain[x]['nb_filleuls'] < 0]}")

    pd.DataFrame().from_dict(res_med_min).T.to_excel('parrainage.xlsx',sheet_name='median',index=False, index_label=False)
    pd.DataFrame().from_dict(res_avg_max).T.to_excel('parrainage.xlsx',sheet_name='mean',index=False, index_label=False,)
