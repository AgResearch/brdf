--
-- Name: $1; Type: FK CONSTRAINT; Schema: public; Owner: agrbrdf
--

ALTER TABLE ONLY commentlink
    ADD CONSTRAINT "$1" FOREIGN KEY (commentob) REFERENCES commentob(obid);


