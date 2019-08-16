--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosequencefact
    ADD CONSTRAINT "$1" FOREIGN KEY (biosequenceob) REFERENCES biosequenceob(obid);


