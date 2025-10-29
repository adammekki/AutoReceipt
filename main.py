import antrag
import hinreise
import ruckreise

if __name__ == "__main__":
    antrag_instance = antrag.antrag()
    hinreise_instance = hinreise.hinreise("")

    print("Starting Antrag process...")
    antrag_instance.main()

    print("Starting Hinreise process...")
    hinreise_instance.main()

    print("Starting Ruckreise process...")
    ruckreise_instance = ruckreise.ruckreise(hinreise_instance.response)
    ruckreise_instance.main()