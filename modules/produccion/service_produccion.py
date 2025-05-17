from .repository_produccion import ProduccionRepository

class ProduccionService:

    @staticmethod
    def agregar(data):
        required_fields = ['fecha', 'producto_id', 'cantidad', 'unidad', 'responsable_id']
        for field in required_fields:
            if not data.get(field):
                return {"error": f"Falta el campo: {field}"}, 400

        return ProduccionRepository.insertar(data)

    @staticmethod
    def listar():
        return ProduccionRepository.listar()
