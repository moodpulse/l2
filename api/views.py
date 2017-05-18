from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import api.models as models
import simplejson as json
import directions.models as directions
import directory.models as directory
import users.models as users
import yaml
from slog import models as slog
from django.utils import timezone

def translit(locallangstring):
    """
    Translit func
    :param locallangstring: orign
    :return: translit of locallangstring
    """
    conversion = {
        u'\u0410' : 'A',    u'\u0430' : 'a',
        u'\u0411' : 'B',    u'\u0431' : 'b',
        u'\u0412' : 'V',    u'\u0432' : 'v',
        u'\u0413' : 'G',    u'\u0433' : 'g',
        u'\u0414' : 'D',    u'\u0434' : 'd',
        u'\u0415' : 'E',    u'\u0435' : 'e',
        u'\u0401' : 'Yo',   u'\u0451' : 'yo',
        u'\u0416' : 'Zh',   u'\u0436' : 'zh',
        u'\u0417' : 'Z',    u'\u0437' : 'z',
        u'\u0418' : 'I',    u'\u0438' : 'i',
        u'\u0419' : 'Y',    u'\u0439' : 'y',
        u'\u041a' : 'K',    u'\u043a' : 'k',
        u'\u041b' : 'L',    u'\u043b' : 'l',
        u'\u041c' : 'M',    u'\u043c' : 'm',
        u'\u041d' : 'N',    u'\u043d' : 'n',
        u'\u041e' : 'O',    u'\u043e' : 'o',
        u'\u041f' : 'P',    u'\u043f' : 'p',
        u'\u0420' : 'R',    u'\u0440' : 'r',
        u'\u0421' : 'S',    u'\u0441' : 's',
        u'\u0422' : 'T',    u'\u0442' : 't',
        u'\u0423' : 'U',    u'\u0443' : 'u',
        u'\u0424' : 'F',    u'\u0444' : 'f',
        u'\u0425' : 'H',    u'\u0445' : 'h',
        u'\u0426' : 'Ts',   u'\u0446' : 'ts',
        u'\u0427' : 'Ch',   u'\u0447' : 'ch',
        u'\u0428' : 'Sh',   u'\u0448' : 'sh',
        u'\u0429' : 'Sch',  u'\u0449' : 'sch',
        u'\u042a' : '',    u'\u044a' : '',
        u'\u042b' : 'Y',    u'\u044b' : 'y',
        u'\u042c' : '',   u'\u044c' : '',
        u'\u042d' : 'E',    u'\u044d' : 'e',
        u'\u042e' : 'Yu',   u'\u044e' : 'yu',
        u'\u042f' : 'Ya',   u'\u044f' : 'ya',
    }
    translitstring = []
    for c in locallangstring:
        translitstring.append(conversion.setdefault(c, c))
    return ''.join(translitstring)

@csrf_exempt
def send(request):
    """
    Sysmex save results
    :param request:
    :return:
    """
    result = {"ok": False}
    try:
        if request.method == "POST":
            resdict = yaml.load(request.POST["result"])
            appkey = request.POST["key"]
        else:
            resdict = yaml.load(request.GET["result"])
            appkey = request.GET["key"]

        astm_user = users.DoctorProfile.objects.filter(user__pk=866).first()
        if "LYMPH%" in resdict["result"]:
            resdict["orders"] = {}

        dpk = -1
        if "bydirection" in request.POST or "bydirection" in request.GET:
            dpk = resdict["pk"]

            if dpk >= 4600000000000:
                dpk -= 4600000000000
                dpk //= 10

            if directions.TubesRegistration.objects.filter(issledovaniya__napravleniye__pk=dpk).exists():
                resdict["pk"] = directions.TubesRegistration.objects.filter(
                    issledovaniya__napravleniye__pk=dpk).first().pk
            else:
                resdict["pk"] = -1
            resdict["bysapphire"] = True

        if resdict["pk"] and models.Application.objects.filter(key=appkey).exists() and directions.TubesRegistration.objects.filter(pk=resdict["pk"]).exists():
            tubei = directions.TubesRegistration.objects.get(pk=resdict["pk"])
            direction = tubei.issledovaniya_set.first().napravleniye
            for key in resdict["result"].keys():
                if models.RelationFractionASTM.objects.filter(astm_field=key).exists():
                    fractionRels = models.RelationFractionASTM.objects.filter(astm_field=key)
                    for fractionRel in fractionRels:
                        fraction = fractionRel.fraction
                        if directions.Issledovaniya.objects.filter(napravleniye=direction,
                                                                   research=fraction.research).exists():
                            issled = directions.Issledovaniya.objects.get(napravleniye=direction,
                                                                          research=fraction.research)
                            fraction_result = None
                            if directions.Result.objects.filter(issledovaniye=issled,
                                                                fraction=fraction).exists():  # Если результат для фракции существует
                                fraction_result = directions.Result.objects.get(issledovaniye=issled,
                                                                                fraction__pk=fraction.pk)  # Выборка результата из базы
                            else:
                                fraction_result = directions.Result(issledovaniye=issled,
                                                                    fraction=fraction)  # Создание нового результата
                            fraction_result.value = resdict["result"][key].strip()  # Установка значения
                            if fractionRel.get_multiplier_display() > 1:
                                if fraction_result.value.isdigit():
                                    fraction_result.value = "%s.0" % fraction_result.value
                                import re
                                find = re.findall("\d+.\d+", fraction_result.value)
                                if len(find) > 0:
                                    val = int(float(find[0]) * fractionRel.get_multiplier_display())
                                    fraction_result.value = fraction_result.value.replace(find[0], str(val))
                            fraction_result.iteration = 1  # Установка итерации
                            fraction_result.save()  # Сохранение
                            fraction_result.issledovaniye.doc_save = astm_user  # Кто сохранил
                            from datetime import datetime
                            fraction_result.issledovaniye.time_save = timezone.now()  # Время сохранения
                            fraction_result.issledovaniye.save()
            slog.Log(key=appkey, type=22, body=json.dumps(resdict), user=astm_user).save()
            result["ok"] = True
        elif not directions.TubesRegistration.objects.filter(pk=resdict["pk"]).exists():
            if dpk > -1:
                resdict["pk"] = dpk
            slog.Log(key=resdict["pk"], type=23, body=json.dumps(resdict), user=astm_user).save()
    except Exception:
        result = {"ok": False, "Exception": True}
    return HttpResponse(json.dumps(result), content_type="application/json")  # Создание JSON


@csrf_exempt
def get_order(request):
    """
    Gen order of direction
    :param request:
    :return:
    """
    import astm
    from time import gmtime, strftime
    sdt = strftime("%Y%m%d%H%M%S", gmtime())
    ra = [["H","\\^&","","",["Host","P_1"],"","","","",["BIOLIS NEO","System1"],"","P","1",sdt]]

    if request.method == "POST":
        sample_id = request.POST["sample_id"]
    else:
        sample_id = request.GET["sample_id"]
    tubei = directions.TubesRegistration.objects.get(pk=sample_id)
    issledovaniya = directions.Issledovaniya.objects.filter(tubes=tubei)
    client = issledovaniya.first().napravleniye.client
    ra.append(["P",
               "1",
               str(client.pk),
               "",
               "",
               [translit(client.family),translit(client.name)],
               "",
               "{}{}{}".format(*client.birthday.split(" ")[0].split(".")[::-1]),
               translit(client.sex.upper()).replace("Zh","F"),
               "",
               "",
               "",
               "",
               "" ])

    inta = 0
    for iss in issledovaniya:
        for fr in directions.directory.Fractions.objects.filter(research=iss.research):
            rel = models.RelationFractionASTM.objects.filter(fraction=fr)
            field = translit(fr.title)
            if rel.exists():
                inta += 1
                field = rel.first().astm_field
                ra.append(["O",str(inta),sample_id,["","0","0"],["","","","", field,"0"],"R","","","","","","N","","","","Serum","","","","","","","","","","O"])
    ra.append(["L","1","N"])
    result = astm.codec.iter_encode(ra)
    return HttpResponse(result, content_type="text/plain")

@csrf_exempt
def results(request):
    """
    Sapphire results save
    :param request:
    :return:
    """
    result = {"ok": False}
    if request.method == "POST":
        resdict = request.POST["result"]
        key = request.POST["key"]
    else:
        resdict = request.GET["result"]
        key = request.GET["key"]
    resdict = json.loads(resdict.replace("'", "\""))

    if key and models.Application.objects.filter(key=key).exists():
        for patient in resdict["PATIENTS"]:
            for order in patient["ORDERS"]:
                for rest in order["RESULTS"]:
                    if patient["ID"] and patient["ID"].isdigit():
                        direction = directions.Issledovaniya.objects.filter(pk=int(patient["ID"])).first().napravleniye
                        if models.RelationFractionASTM.objects.filter(astm_field=rest["TEST"]["ITEM_NAME"]).exists():
                            fractionRels = models.RelationFractionASTM.objects.filter(astm_field=rest["TEST"]["ITEM_NAME"])
                            for fractionRel in fractionRels:
                                fraction = fractionRel.fraction
                                if directions.Issledovaniya.objects.filter(napravleniye=direction,
                                                                           research=fraction.research).exists():
                                    issled = directions.Issledovaniya.objects.get(napravleniye=direction,
                                                                                  research=fraction.research)
                                    fraction_result = None
                                    if directions.Result.objects.filter(issledovaniye=issled,
                                                                        fraction=fraction).exists():  # Если результат для фракции существует
                                        fraction_result = directions.Result.objects.get(issledovaniye=issled,
                                                                                        fraction__pk=fraction.pk)  # Выборка результата из базы
                                    else:
                                        fraction_result = directions.Result(issledovaniye=issled,
                                                                            fraction=fraction)  # Создание нового результата
                                    fraction_result.value = rest["VALUE"].strip()  # Установка значения
                                    if fractionRel.get_multiplier_display() > 1:
                                        import re
                                        find = re.findall("\d+.\d+", fraction_result.value)
                                        if len(find) > 0:
                                            val = int(float(find[0]) * fractionRel.get_multiplier_display())
                                            fraction_result.value = fraction_result.value.replace(find[0], str(val))
                                    fraction_result.iteration = 1  # Установка итерации
                                    fraction_result.save()  # Сохранение
                                    fraction_result.issledovaniye.doc_save = users.DoctorProfile.objects.filter(
                                            user__pk=866).first()  # Кто сохранил
                                    from datetime import datetime
                                    fraction_result.issledovaniye.time_save = timezone.now()  # Время сохранения
                                    fraction_result.issledovaniye.save()
        result["ok"] = True
    return HttpResponse(json.dumps(result), content_type="application/json")  # Создание JSON


@csrf_exempt
def results_normal(request):
    """
    Sapphire results save normal (test)
    :param request:
    :return:
    """
    result = {"ok": False}
    if request.method == "POST":
        resdict = request.POST["result"]
        key = request.POST["key"]
    else:
        resdict = request.GET["result"]
        key = request.GET["key"]
    resdict = json.loads(resdict.replace("'", "\""))
    if key and models.Application.objects.filter(key=key).exists():
        for patient in resdict["PATIENTS"]:
            for order in patient["ORDERS"]:
                for rest in order["RESULTS"]:
                    if order["SAMPLE_ID"] and order["SAMPLE_ID"].isdigit():
                        tubei = directions.TubesRegistration.objects.get(pk=order["SAMPLE_ID"])
                        direction = directions.Issledovaniya.objects.filter(tubes=tubei).first().napravleniye
                        if models.RelationFractionASTM.objects.filter(astm_field=rest["TEST"]["ITEM_NAME"]).exists():
                            fractionRels = models.RelationFractionASTM.objects.filter(astm_field=rest["TEST"]["ITEM_NAME"])
                            for fractionRel in fractionRels:
                                fraction = fractionRel.fraction
                                if directions.Issledovaniya.objects.filter(napravleniye=direction,
                                                                           research=fraction.research).exists():
                                    issled = directions.Issledovaniya.objects.get(napravleniye=direction,
                                                                                  research=fraction.research)
                                    fraction_result = None
                                    if directions.Result.objects.filter(issledovaniye=issled,
                                                                        fraction=fraction).exists():  # Если результат для фракции существует
                                        fraction_result = directions.Result.objects.get(issledovaniye=issled,
                                                                                        fraction__pk=fraction.pk)  # Выборка результата из базы
                                    else:
                                        fraction_result = directions.Result(issledovaniye=issled,
                                                                            fraction=fraction)  # Создание нового результата
                                    fraction_result.value = rest["VALUE"].strip()  # Установка значения
                                    if fractionRel.get_multiplier_display() > 1:
                                        import re
                                        find = re.findall("\d+.\d+", fraction_result.value)
                                        if len(find) > 0:
                                            val = int(float(find[0]) * fractionRel.get_multiplier_display())
                                            fraction_result.value = fraction_result.value.replace(find[0], str(val))
                                    fraction_result.iteration = 1  # Установка итерации
                                    fraction_result.save()  # Сохранение
                                    fraction_result.issledovaniye.doc_save = users.DoctorProfile.objects.filter(
                                            user__pk=866).first()  # Кто сохранил
                                    from datetime import datetime
                                    fraction_result.issledovaniye.time_save = timezone.now()  # Время сохранения
                                    fraction_result.issledovaniye.save()
        result["ok"] = True
    return HttpResponse(json.dumps(result), content_type="application/json")  # Создание JSON
