from database.parco_DAO import ParcoDAO
from database.escursione_DAO import EscursioneDAO
from database.punto_interesse_DAO import PuntoInteresseDAO
from model import escursione, punto_interesse


class Model:
    def __init__(self):
        self._max_budget = None
        self._max_giorni = None
        self.escursioni_map = {}
        self.punti_interesse_map = {}
        self._pacchetto_ottimo = []
        self._valore_ottimo: int = -1
        self._costo = 0
        self._escursioni_parco = []



        # Caricamento
        self.load_escursioni()
        self.load_punti_interesse()
        self.load_relazioni()

    @staticmethod
    def load_parchi():
        """ Restituisce tutti i parchi disponibili """
        return ParcoDAO.get_parchi()

    def load_escursioni(self):
        """ Carica tutte le escursioni in un dizionario [id, Escursione]"""
        self.escursioni_map = EscursioneDAO.get_escursioni()

    def load_punti_interesse(self):
        """ Carica tutti i punti di interesse in un dizionario [id, PuntoInteresse]"""
        self.punti_interesse_map = PuntoInteresseDAO.get_punti_interesse()

    def load_relazioni(self):
        """
            Interroga il database per ottenere tutte le relazioni fra escursioni e punti di interesse e salvarle nelle strutture dati
            Collega escursione <-> punti di interesse.
            --> Ogni Escursione ha un set di PuntoInteresse.
            --> Ogni PuntoInteresse ha un set di Escursioni.
        """
        relazione = EscursioneDAO.get_escursioni_punti_interesse()
        for r in relazione:
            escursioni = self.escursioni_map[r['id_escursione']]
            punti_interesse = self.punti_interesse_map[r['id_punto_interesse']]
            escursioni.punti_interesse.add(punti_interesse)
            punti_interesse.escursioni.add(escursioni)





    def genera_pacchetto(self, id_parco: str, max_giorni: int = None, max_budget: float = None):
        """
        Calcola il pacchetto di escursioni ottimale per un parco rispettando i vincoli di durata, budget e punti di interesse unici.
        :param id_parco: id del parco
        :param max_giorni: numero massimo di giorni (può essere None --> nessun limite)
        :param max_budget: costo massimo del pacchetto (può essere None --> nessun limite)

        :return: self._pacchetto_ottimo (una lista di oggetti Escursione)
        :return: self._costo (il costo del pacchetto)
        :return: self._valore_ottimo (il voto complessivo dei visitatori per il pacchetto)
        """
        self._pacchetto_ottimo = []
        self._costo = 0
        self._valore_ottimo = -1
        self._escursioni_parco = []
        for e in self.escursioni_map.values():
            if e.id_parco == id_parco:
                self._escursioni_parco.append(e)


        self._max_giorni = max_giorni
        self._max_budget = max_budget
        self._ricorsione(0,[],0,0, 0, set())



        return self._pacchetto_ottimo, self._costo, self._valore_ottimo

    def _is_valid(self, esc, durata_corrente, costo_corrente, punti_usati):
        if self._max_giorni is not None:
            if durata_corrente + esc.durata_giorni > self._max_giorni:
                return False
        if self._max_budget is not None:
            if costo_corrente + esc.costo > self._max_budget:
                return False
        for punto in esc.punti_interesse:
            if punto in punti_usati:
                return False
        return True


    def _ricorsione(self,start_index: int, pacchetto_parziale: list, durata_corrente: int, costo_corrente: float, valore_corrente: int, punti_usati: set):
        """ Algoritmo di ricorsione che deve trovare il pacchetto che massimizza il voto complessivo dei visitatori"""
        if valore_corrente > self._valore_ottimo :
            self._valore_ottimo = valore_corrente
            self._costo = costo_corrente
            self._pacchetto_ottimo = pacchetto_parziale.copy()

        if start_index == len(self._escursioni_parco) :
            return

        else:
            for i in range (start_index, len(self._escursioni_parco)):
                esc = self._escursioni_parco[i]
                if self._is_valid(esc, durata_corrente, costo_corrente, punti_usati):
                    valore_aggiunto = 0
                    for punto in esc.punti_interesse:
                        valore_aggiunto += punto.voto_visitatori
                    nuova_durata = durata_corrente + esc.durata_giorni
                    nuovo_costo = costo_corrente + esc.costo
                    nuovo_valore = valore_corrente + valore_aggiunto

                    pacchetto_parziale.append(esc)
                    for punto in esc.punti_interesse:
                        punti_usati.add(punto)

                    self._ricorsione(
                        i + 1,
                        pacchetto_parziale,
                        nuova_durata,
                        nuovo_costo,
                        nuovo_valore,
                        punti_usati
                    )
                    pacchetto_parziale.pop()
                    for punto in esc.punti_interesse:
                        punti_usati.remove(punto)







