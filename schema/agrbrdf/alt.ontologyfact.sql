--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY ontologyfact
    ADD CONSTRAINT "$1" FOREIGN KEY (ontologyob) REFERENCES ontologyob(obid);


