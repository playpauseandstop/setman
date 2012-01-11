from setman import settings


__all__ = ('update_form_fields', )


def update_form_fields(form):
    """
    After bounding WTForms forgot about all custom field attributes like
    ``app_name``, so we need to repeat some form building here.
    """
    unbound_form_fields = settings._framework.build_form_fields()

    for field in form:
        unbound_field = unbound_form_fields.get(field.name, None)

        if unbound_field:
            field.app_name = unbound_field.app_name

    return form
