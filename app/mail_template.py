"""
AWS SES BODY_HTML templates
"""


def create_submission_mail_SES(submission):
    """
    Bejelentéskor kimenő email
    """
    return f"""<h3>Szia!</h3>
              <p>Köszi, hogy jelezted nekünk az alábbi problémát: {submission.title}<br>
                 4000 mérnökünk és 3600 menyétünk elkezdett dolgozni rajta.<br>Hamarosan megoldjuk, vagy nem.
              </p>
              <p>Keresünk majd, amint kitaláltuk, hogy mit csináljunk a dologgal.<br>
              Addig is itt tudod nyomonkövetni, hogyan állunk vele: https://rendkivuliugyek.com/single_submission/{submission.id}</p>
              <p><b>Rendkívüli Ügyek Minisztériuma</b></p>                            
           """


def create_status_change_mail_SES(submission):
    """
    Státusz változáskor kimenő email
    """
    return f"""<h3>Szia!</h3>
	       <p>A {submission.title} ügy státusza megváltozott a következőre: {submission.status}</p>
	       <p>Az ügy adatlapját itt találod:</p>
	       <p>https://rendkivuliugyek.com/single_submission/{submission.id}</p>
	       <p><b>Rendkívüli Ügyek Minisztériuma</b></p>
	    """


def create_solution_mail_SES(submission):
    """
    Ügy lezárásakor kimenő email
    """
    return f"""<h3>Szia!</h3>
               <p>Jó hír: sikerült megoldanunk a problémát, amit bejelentettél: {submission.title}</p>
               <p>Itt tudod megnézni, hogy mire jutottunk: https://rendkivuliugyek.com/single_submission/{submission.id}</p>
               <p><b>Rendkívüli Ügyek Minisztériuma</b></p>
            """


def create_organiser_mail_SES(submission):
    """
    Szervező_hozzáadásakor kimenő email
    """
    return f"""<h2>Gratulálunk!</h2>
               <h3>Szervezőként lettél beállítva
               a Rendkívüli Ügyek Minisztériumának következő bejelentésénél:
               </h3>
               <p>{submission.title}</p>
               <p>https://rendkivuliugyek.com/single_submission/{submission.id}</p>
               <p><b>Rendkívüli Ügyek Minisztériuma</b></p>
           """
