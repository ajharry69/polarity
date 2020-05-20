"""
create hashed temporary password

```python

temp_pass = get_user_model().objects.get_random_password(length=random.randint(8,10))
user = get_user_model().objects.get_by_natural_key(username='username')
user.set_password(temp_pass)
meta = UserMetadata.objects.get_or_create(user=user,password=user.password)

```
"""
from django.shortcuts import render

# Create your views here.
