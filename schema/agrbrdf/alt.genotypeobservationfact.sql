--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY genotypeobservationfact
    ADD CONSTRAINT "$1" FOREIGN KEY (genotypeobservation) REFERENCES genotypeobservation(obid);


