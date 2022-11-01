"""
Email templates
"""

def create_submission_mail(submission, from_mail, to_mail):
   """
   """
   return {'Messages': [
            {
            "From": {
            "Email": f"{from_mail}",
            "Name":  "MKKP"
              },
              "To": [
            {
              "Email": f"{to_mail}",
              "Name":  "MKKP"
            }
              ],
              "Subject":  "Sikeres városmódosító bejelentés!",
              "TextPart": "Sikeres városmódosító bejelentés!",
              "HTMLPart": f"""<h3>Szia!</h3>
                              <p>Köszi, hogy jelezted nekünk az alábbi problémát: {submission.title}<br>
                              4000 mérnökünk és 3600 menyétünk elkezdett dolgozni rajta.<br>Hamarosan megoldjuk, vagy nem.
                              </p>
                              <p>Keresünk majd, amint kitaláltuk, hogy mit csináljunk a dologgal.<br>
                              Addig is itt tudod nyomonkövetni, hogyan állunk vele: https://rendkivuliugyek.site/single_submission/{submission.id}</p>
		              <p><b>Rendkívüli Ügyek Minisztériuma</b></p>                            
                              """,
              "CustomID": "MKKP városmódosító bejelentés"
            }
          ]
        }


def create_status_change_mail(submission, from_mail):
    """
    """
    return {'Messages': [
		    {
		    "From": {
		    "Email": f"{from_mail}",
		    "Name":  "MKKP"
		      },
		      "To": [
		    {
		      "Email": f"{submission.owner_email}",
		      "Name":  "MKKP"
		    }
		      ],
		      "Subject":  f"Státusz változás: {submission.title}",
		      "TextPart": "Városfelújítós ügy státusz változás",
		      "HTMLPart": f"""<h3>Kedves {submission.owner_user}!</h3>
		                      <p>A {submission.title} ügy státusza megváltozott a következőre: {submission.status}
		                      </p>
		                      <p>Az ügy adatlapját itt találod:</p>
		                      <p>https://rendkivuliugyek.site/single_submission/{submission.id}</p>
			              <p><b>Rendkívüli Ügyek Minisztériuma</b></p>
		                      """,
		      "CustomID": "MKKP városmódosító bejelentés"
		    }
		  ]
		}
		
def create_solution_mail(submission, from_mail):
    """
    """
    return {'Messages': [
	    {
	    "From": {
	    "Email": f"{from_mail}",
	    "Name":  "MKKP"
	      },
	      "To": [
	    {
	      "Email": f"{submission.submitter_email}",
	      "Name":  "MKKP"
	    }
	      ],
	      "Subject":  f"Befejezett ügy: {submission.title}",
	      "TextPart": "Befejezett ügy",
	      "HTMLPart": f"""<h3>Szia!</h3>
			      <p>Jó hír: sikerült megoldanunk a problémát, amit bejelentettél: {submission.title}</p>
			      <p>Itt tudod megnézni, hogy mire jutottunk: https://rendkivuliugyek.site/single_submission/{submission.id}</p>
			      <p><b>Rendkívüli Ügyek Minisztériuma</b></p>
			      """,
	      "CustomID": "MKKP városmódosító bejelentés"
	      }
	    ]
	   }
	   
def create_organiser_mail(submission, from_mail, to_mail):
    """
    """
    return {'Messages': [
            {
            "From": {
            "Email": f"{from_mail}",
            "Name":  "MKKP"
              },
              "To": [
            {
              "Email": f"{to_mail}",
              "Name":  "MKKP"
            }
              ],
              "Subject":  "MKKP szervező lettél!",
              "TextPart": "MKKP szervező lettél!",
              "HTMLPart": f"""<h2>Gratulálunk!</h2>
              <h3>Szervezőként lettél beállítva
               a Rendkívüli Ügyek Minisztériumának következő bejelentésénél:</h3>
              <p>{submission.title}</p>
              <p>https://rendkivuliugyek.site/single_submission/{submission.id}</p>
              <p><b>Rendkívüli Ügyek Minisztériuma</b></p>
              """,
              "CustomID": "MKKP szervező lettél!"
            }
          ]
        }	   		
