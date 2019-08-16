--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosequencefeatureattributefact
    ADD CONSTRAINT "$1" FOREIGN KEY (biosequencefeaturefact) REFERENCES biosequencefeaturefact(obid);


