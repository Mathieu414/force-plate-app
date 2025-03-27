## Plateforme de force

### Caractéristiques de la plateforme de force

La plateforme de force renvoit des valeurs en Volt, des valeurs ANALOGIQUES, qui sont ensuites converties à l'aide d'un boitier NI (Nationals Instruments).
Ces valeurs dépendent de la configuration du boitier Kisler qui sert de transformateur au niveau de la plateforme de force.
4 valeurs sont possibles pour l'étalonage : 250N/500N/2,5kN et 5kN.

L'unité de sortie de la plateforme est en **Volt**. Qu'il faut ensuite convertir en N avant de basculer en grammes :

$$
masse = tension*1/sensitivité*1/gravité
$$

> A noter : $N = kg.m.s^{-2}$

> Force gravitationelle : $g = 9.80665 m.s^{-2}$

Les informations diverses de la plateforme sont ci-dessous :

#### 1. Gamme étalonnée (3 Fx, Fy, Fz) :

La plaque est étalonnée pour mesurer les forces selon trois axes :

- Fx, Fy (horizontal) : ±2,5 kN (kilonewtons).
- Fz (vertical) : de 0 à 10 kN.

#### 2. Gamme de sensibilité :

La sortie de tension par unité de force appliquée :

Sensibilité de la gamme 1 (plus élevée) :

- Fx, Fy : ~403 mV/N (millivolts par newton).
- Fz : ~183 mV/N.

Sensibilité de la gamme 4 (plus faible) :

- Fx, Fy : ~2,03 mV/N.
- Fz : ~0,93 mV/N.

#### 3. Rapports de gamme (1:2:3:4) :

La plaque de force dispose de ratios de sensibilité sélectionnables, avec des rapports de 1:5:10:20 pour des résolutions de mesure de force différentes.

#### 4. Seuil :

La plus petite force mesurable est <250 mN (millinewtons), indiquant le seuil de sensibilité avant que le bruit n'affecte la précision.

#### 5. Dérive :

La dérive du signal est <±10 mN/s, assurant une stabilité dans le temps, ce qui est particulièrement important pour des mesures de longue durée.

#### 6. Tension et courant d'alimentation :

Nécessite une alimentation de 10-30 V DC et consomme environ 45 mA pour fonctionner.
