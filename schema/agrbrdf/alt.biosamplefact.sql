--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY biosamplefact
    ADD CONSTRAINT "$1" FOREIGN KEY (biosampleob) REFERENCES biosampleob(obid);


