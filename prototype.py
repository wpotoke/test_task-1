import argparse
import json



class FileHandler:

    def __init__(self, files):
        self.files = files
    

    def resolve_rate(self, data, key):
        valid_value = ["rate", "hourly_rate", "hourly_rat", "salary"]

        for i in valid_value:
            if i in data[key]:
                return i
        return None
    
    def create_paremetrs(self, file):
        file.seek(0)
        data = {f'employee_{i + 1}': None for i in range(len(file.readlines()) - 1)}
        file.seek(0)
        keys = [i for i in file.readlines()[0].strip().split(',')]
        file.seek(0)
        values = [i.strip().split(',')for i in file.readlines()[1:]]
        file.seek(0)
        return data, keys, values


    def handle(self):

        dict_output = {}
        
        for file in self.files:
            with open(file, 'r', encoding='utf-8') as file:
                data, keys, values = self.create_paremetrs(file)

                for i, k in enumerate(data):
                    data[k] = {keys[item]: values[i][item] for item in range(len(keys))}
                    rate = self.resolve_rate(data, k)
                    data[k]['payout'] = '$' + str(int(data[k]["hours_worked"]) * int(data[k][rate]))

                departments_payout = {data[i]['department']: 0 for i in data}
                department_hours = {data[i]['department']: 0 for i in data}
                department_names = sorted(list(set([data[i]['department'] for i in data])))
                for i in data:
                    departments_payout[data[i]['department']] += int(data[i]['payout'][1:])
                    department_hours[data[i]['department']] += int(data[i]['hours_worked'])

                
                
                for i in data.values():
                    if i['department'] in department_names:
                        if i['department'] not in dict_output:
                            dict_output[i['department']] = [{'name': i['name'],
                                                'hours': i['hours_worked'],
                                                'rate': i[rate],
                                                'payout': i['payout']}]
                        else:
                            dict_output[i['department']].append({'name': i['name'],
                                                'hours': i['hours_worked'],
                                                'rate': i[rate],
                                                'payout': i['payout']})
                for k, v in department_hours.items():
                    dict_output[k].append({'total_hours': str(v)})

                for k, v in departments_payout.items():
                    dict_output[k].append({'total_payout':'$' + str(v)})
                
                
                result = json.dumps(dict_output, indent=4, ensure_ascii=False)
                print(result)
                dict_output = {}
                

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Csv to json')

    parser.add_argument('files', 
                        nargs='+',
                        help='Список файлов')
    parser.add_argument(
        '--report',
        type=str,
        required=True,
        help='Название отчёта (например: payout)'
    )

    args = parser.parse_args()
    files = args.files
    test = FileHandler(files)
    if args.report == "payout":
        test.handle()
    else:
        print(f"⚠️ Отчёт '{args.report}' не поддерживается")