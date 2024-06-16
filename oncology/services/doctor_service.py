from oncology.models import Doctor


def get_doctor_by_email(email):
    return Doctor.objects.get(email=email)


def set_doctor_password(request):
    user = get_doctor_by_email(request.data['email'])
    user.set_password(request.data['password'])
    user.is_active = True
    user.save()

    return user
