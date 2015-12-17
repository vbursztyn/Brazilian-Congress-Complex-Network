import pickle
import matplotlib.pyplot as plt

avg_w = dict()
same_party_avg_w = dict()
same_state_avg_w = dict()

with open('codonators_net.p') as f_codonators:
	records = pickle.load(f_codonators)
	for record in records:
		if record[0] not in avg_w:
			avg_w[record[0]] = list()
			same_party_avg_w[record[0]] = list()
			same_state_avg_w[record[0]] = list()
		if record[1] not in avg_w:
			avg_w[record[1]] = list()
			same_party_avg_w[record[1]] = list()
			same_state_avg_w[record[1]] = list()

		s1 = record[0].split('(')[1].split('-')[0]
		s2 = record[1].split('(')[1].split('-')[0]
		p1 = record[0].split('(')[1].split('-')[1]
		p2 = record[1].split('(')[1].split('-')[1]

		if s1 == s2:
			same_state_avg_w[record[0]].append(record[2])
			same_state_avg_w[record[1]].append(record[2])
		if p1 == p2:
			same_party_avg_w[record[0]].append(record[2])
			same_party_avg_w[record[1]].append(record[2])

		avg_w[record[0]].append(record[2])
		avg_w[record[1]].append(record[2])


same_state_gain = dict()
same_party_gain = dict()

for congressman in avg_w:
	avg_w[congressman] = sum(avg_w[congressman]) / float(len(avg_w[congressman]))
	if len(same_state_avg_w[congressman]):
		same_state_avg_w[congressman] = sum(same_state_avg_w[congressman]) / float(len(same_state_avg_w[congressman]))
		same_state_gain[congressman] = (same_state_avg_w[congressman] - avg_w[congressman]) / avg_w[congressman]
	if len(same_party_avg_w[congressman]):
		same_party_avg_w[congressman] = sum(same_party_avg_w[congressman]) / float(len(same_party_avg_w[congressman]))
		same_party_gain[congressman] = (same_party_avg_w[congressman] - avg_w[congressman]) / avg_w[congressman]


plt.title('Jaccard (more similar donors) gain derived from co-regionality')
plt.bar(range(len(same_state_gain)), same_state_gain.values(), align='center', alpha=0.7, color='black'	)
plt.xticks(range(len(same_state_gain)), same_state_gain.keys(), rotation='vertical')
plt.show()

print 'Regarding similar donors...'
avg_same_state_gain = 0.0
for gain in same_state_gain.values():
	avg_same_state_gain += gain
print 'Average Jaccard gain derived from co-regionality: %s' %(avg_same_state_gain / len(same_state_gain))


plt.title('Jaccard gain (more similar donors) derived from co-partisanship')
plt.bar(range(len(same_party_gain)), same_party_gain.values(), align='center', alpha=0.7, color='black')
plt.xticks(range(len(same_party_gain)), same_party_gain.keys(), rotation='vertical')
plt.show()

avg_same_party_gain = 0.0
for gain in same_party_gain.values():
	avg_same_party_gain += gain
print 'Average Jaccard gain derived from co-partisanship: %s' %(avg_same_party_gain / len(same_party_gain))

