from wtforms import fields
from wtforms.validators import Required as BaseRequired


__all__ = ('Required', )


class Required(BaseRequired):
    """
    No, seriously, int(0), float(0), Decimal(0) is perfectly valid required
    values for Integer, Float or Decimal fields.
    """
    def __call__(self, form, field):
        """
        Fix default behaviour in direct way by checking field type.
        """
        zero_fields = (fields.DecimalField,
                       fields.FloatField,
                       fields.IntegerField)

        for zero_field in zero_fields:
            if isinstance(field, zero_field) and field.data == 0:
                return True

        return super(Required, self).__call__(form, field)
