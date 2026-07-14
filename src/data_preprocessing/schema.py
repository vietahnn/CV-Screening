class Candidate:
    def __init__(self, id, candidate_name,email,social_links,resume, filename=None):
        self.id = id
        self.resume = resume
        self.candidate_name = candidate_name
        self.email = email
        self.social_links = social_links
        self.filename = filename

    def to_dict(self):
        return {
            "id": self.id,
            "name" : self.candidate_name,
            "email":self.email,
            "social_links": self.social_links,
            "resume": self.resume,
            "filename": self.filename
        }

    def __repr__(self):
        return f"Candidate_id : {self.id}\n Resume: \n{self.resume}\n"           